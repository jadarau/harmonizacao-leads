from __future__ import annotations

from app.services.kafka_consumer import ClientesKafkaConsumer
from app.models.client import Cliente


def test_map_payload_to_cliente_varied_keys():
    payload = {
        "name": "Ana Teste",
        "phones": ["(11) 98765-4321"],
        "emails": ["ana@example.com"],
        "birthdate": "1992-01-10",
        "source": "formulario",
        "addresses": [
            {
                "logradouro": "Av. Central",
                "numero": "100",
                "bairro": "Centro",
                "cidade": "São Paulo",
                "estado": "SP",
                "cep": "01001000",
                "tipo": "residencial",
            }
        ],
    }

    mapped = ClientesKafkaConsumer._map_payload_to_cliente(payload)
    c = Cliente(**mapped)

    assert c.nome == "Ana Teste"
    assert c.telefone == ["11987654321"]
    assert c.email == ["ana@example.com"]
    assert c.nascimento == "1992-01-10"
    assert c.origem == "formulario"
    assert c.enderecos and c.enderecos[0].cep == "01001000"


def test_map_payload_to_cliente_exact_keys():
    payload = {
        "nome": "Bruno",
        "telefone": "11999998888",
        "email": "bruno@example.com",
        "nascimento": "1990-12-31",
        "origem": "ads",
        "enderecos": [
            {
                "logradouro": "Rua A",
                "bairro": "B",
                "cidade": "C",
                "estado": "SP",
                "cep": "12345678",
            }
        ],
    }

    mapped = ClientesKafkaConsumer._map_payload_to_cliente(payload)
    c = Cliente(**mapped)
    assert c.nome == "Bruno"
    assert c.telefone == ["11999998888"]
    assert c.email == ["bruno@example.com"]
    assert c.nascimento == "1990-12-31"
    assert c.origem == "ads"