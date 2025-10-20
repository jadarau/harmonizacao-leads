from __future__ import annotations
import asyncio
import json
import logging
from typing import Optional

from app.core.config import settings
from app.database.mongodb import get_database
from app.database.repository import ClienteRepository
from app.models.client import Cliente
import importlib
import ssl

logger = logging.getLogger(__name__)


class ClientesKafkaConsumer:
    """Kafka consumer para o tópico 'clientes'.

    Espera mensagens JSON com o seguinte formato (exemplo):
    {
        "nome": "João Silva",
        "telefone": ["11987654321"],
        "email": ["joao@example.com"],
        "nascimento": "1990-05-15",
        "origem": "website",
        "enderecos": [
            {
                "logradouro": "Rua X",
                "numero": "123",
                "bairro": "Centro",
                "cidade": "São Paulo",
                "estado": "SP",
                "cep": "01001000",
                "tipo": "residencial"
            }
        ]
    }
    """

    def __init__(
        self,
        bootstrap_servers: str,
        group_id: str = "harmonizacao-clientes-consumer",
        topic: str = "clientes",
        ssl: bool = False,
        ssl_cafile: Optional[str] = None,
        ssl_certfile: Optional[str] = None,
        ssl_keyfile: Optional[str] = None,
        enable_auto_commit: bool = True,
        auto_offset_reset: str = "latest",
    ) -> None:
        self._bootstrap_servers = bootstrap_servers
        self._group_id = group_id
        self._topic = topic
        self._enable_auto_commit = enable_auto_commit
        self._auto_offset_reset = auto_offset_reset
        self._task: Optional[asyncio.Task] = None
        self._consumer = None  # type: ignore
        self._stopping = asyncio.Event()
        self._ssl_context = None
        self._ssl_enabled = ssl
        self._ssl_cafile = ssl_cafile
        self._ssl_certfile = ssl_certfile
        self._ssl_keyfile = ssl_keyfile

    async def start(self) -> None:
        logger.info("Iniciando Kafka consumer para tópico '%s'", self._topic)
        try:
            aiokafka = importlib.import_module("aiokafka")
        except Exception as e:
            logger.error("aiokafka não está instalado ou falhou ao importar: %s", e)
            raise

        if self._ssl_enabled:
            context = ssl.create_default_context(cafile=self._ssl_cafile) if self._ssl_cafile else ssl.create_default_context()
            if self._ssl_certfile and self._ssl_keyfile:
                try:
                    context.load_cert_chain(certfile=self._ssl_certfile, keyfile=self._ssl_keyfile)
                except Exception:
                    logger.exception("Falha ao carregar cadeia de certificados SSL")
                    raise
            self._ssl_context = context

        self._consumer = aiokafka.AIOKafkaConsumer(
            self._topic,
            bootstrap_servers=self._bootstrap_servers,
            group_id=self._group_id,
            enable_auto_commit=self._enable_auto_commit,
            auto_offset_reset=self._auto_offset_reset,
            security_protocol="SSL" if self._ssl_context else "PLAINTEXT",
            ssl_context=self._ssl_context,
            value_deserializer=lambda v: v.decode("utf-8") if v is not None else None,
        )
        await self._consumer.start()
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        logger.info("Parando Kafka consumer de '%s'", self._topic)
        self._stopping.set()
        if self._task:
            await self._task
        if self._consumer:
            await self._consumer.stop()
        logger.info("Kafka consumer parado")

    async def _run(self) -> None:
        assert self._consumer is not None
        db = get_database()
        repo = ClienteRepository(db)

        while not self._stopping.is_set():
            try:
                batches = await self._consumer.getmany(timeout_ms=1000, max_records=50)
            except Exception as e:
                if self._stopping.is_set():
                    break
                logger.exception("Erro ao consumir mensagem do Kafka: %s", e)
                await asyncio.sleep(1)
                continue

            for _tp, records in batches.items():
                for record in records:
                    raw_value = record.value
                    if raw_value is None:
                        logger.warning("Mensagem vazia recebida em '%s'", self._topic)
                        continue

                    try:
                        payload = json.loads(raw_value)
                    except json.JSONDecodeError:
                        logger.exception("Falha ao decodificar JSON da mensagem: %s", raw_value)
                        continue

                    mapped = self._map_payload_to_cliente(payload)

                    try:
                        cliente = Cliente(**mapped)
                    except Exception:
                        logger.exception("Payload inválido para Cliente: %s", payload)
                        continue

                    try:
                        # Verifica duplicidade por email
                        exists = False
                        for mail in cliente.email:
                            if mail:
                                found = await repo.get_by_email(mail)
                                if found:
                                    exists = True
                                    logger.info("Cliente já existe com email=%s; ignorando criação", mail)
                                    break
                        # Verifica duplicidade por telefone
                        if not exists:
                            for tel in cliente.telefone:
                                if tel:
                                    found = await repo.get_by_telefone(tel)
                                    if found:
                                        exists = True
                                        logger.info("Cliente já existe com telefone=%s; ignorando criação", tel)
                                        break

                        if not exists:
                            cliente_id = await repo.create(cliente)
                            logger.info(
                                "Cliente criado a partir do Kafka. id=%s nome=%s",
                                cliente_id,
                                cliente.nome,
                            )
                    except Exception:
                        logger.exception("Erro ao salvar/validar cliente no banco para payload: %s", payload)

    @staticmethod
    def _ensure_list(value):
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]

    @classmethod
    def _map_payload_to_cliente(cls, payload: dict) -> dict:
        # Aceita tanto chaves em português quanto alternativas
        telefone = (
            payload.get("telefone")
            or payload.get("telefones")
            or payload.get("phone")
            or payload.get("phones")
        )
        email = payload.get("email") or payload.get("emails")
        enderecos = payload.get("enderecos") or payload.get("addresses")

        mapped = {
            "nome": payload.get("nome") or payload.get("name"),
            "telefone": cls._ensure_list(telefone),
            "email": cls._ensure_list(email),
            "nascimento": payload.get("nascimento")
            or payload.get("data_nascimento")
            or payload.get("birthdate"),
            "origem": payload.get("origem") or payload.get("source"),
            "enderecos": cls._ensure_list(enderecos),
        }
        return mapped


_consumer_instance: Optional[ClientesKafkaConsumer] = None


async def start_kafka_consumer_if_enabled() -> None:
    """Inicializa o consumer se as configs KAFKA estiverem habilitadas."""
    global _consumer_instance

    # Configurações via env
    enabled = getattr(settings, "kafka_enabled", False)
    if not enabled:
        logger.info("Kafka consumer desabilitado (KAFKA_ENABLED=false)")
        return

    bootstrap = getattr(settings, "kafka_bootstrap_servers", None)
    if not bootstrap:
        logger.warning("Kafka habilitado, mas KAFKA_BOOTSTRAP_SERVERS não foi definido.")
        return

    group_id = getattr(settings, "kafka_group_id", "harmonizacao-clientes-consumer")
    topic = getattr(settings, "kafka_clientes_topic", "clientes")
    auto_offset_reset = getattr(settings, "kafka_auto_offset_reset", "latest")

    ssl_enabled = getattr(settings, "kafka_ssl", False)
    ssl_cafile = getattr(settings, "kafka_ssl_cafile", None)
    ssl_certfile = getattr(settings, "kafka_ssl_certfile", None)
    ssl_keyfile = getattr(settings, "kafka_ssl_keyfile", None)

    _consumer_instance = ClientesKafkaConsumer(
        bootstrap_servers=bootstrap,
        group_id=group_id,
        topic=topic,
        ssl=ssl_enabled,
        ssl_cafile=ssl_cafile,
        ssl_certfile=ssl_certfile,
        ssl_keyfile=ssl_keyfile,
        auto_offset_reset=auto_offset_reset,
    )
    await _consumer_instance.start()


async def stop_kafka_consumer() -> None:
    global _consumer_instance
    if _consumer_instance:
        await _consumer_instance.stop()
        _consumer_instance = None
