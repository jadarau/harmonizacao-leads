from __future__ import annotations
import asyncio
import json
import os

try:
    from aiokafka import AIOKafkaProducer
except Exception:
    AIOKafkaProducer = None


async def main():
    if AIOKafkaProducer is None:
        raise RuntimeError("aiokafka não está instalado. Execute: pip install aiokafka")

    bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    topic = os.getenv("KAFKA_CLIENTES_TOPIC", os.getenv("KAFKA_TOPIC_CLIENTE", "clientes"))

    producer = AIOKafkaProducer(
        bootstrap_servers=bootstrap,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    await producer.start()
    try:
        msg = {
            "cliente": {
                "name": "Teste Producer",
                "phones": ["(11) 99999-8888"],
                "emails": ["producer@example.com"],
                "birthdate": "1990-05-15",
                "source": "script",
                "addresses": [
                    {
                        "logradouro": "Rua Produtor",
                        "bairro": "Centro",
                        "cidade": "São Paulo",
                        "estado": "SP",
                        "cep": "01001000",
                    }
                ],
            }
        }
        metadata = await producer.send_and_wait(topic, msg)
        print(
            f"Mensagem enviada para {metadata.topic} [partition={metadata.partition}, offset={metadata.offset}]"
        )
    finally:
        await producer.stop()


if __name__ == "__main__":
    asyncio.run(main())
