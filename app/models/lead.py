from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from .client import Cliente
from .nutricao import Nutricao
from .procedimento import Procedimento

class Lead(BaseModel):
    """Modelo para representar um lead de vendas."""
    id: int = Field(..., description="Identificador numérico único do lead")
    cliente: Cliente = Field(..., description="Dados do cliente associado ao lead")
    data_inicio: datetime = Field(..., description="Data de início do lead")
    data_venda: Optional[datetime] = Field(None, description="Data em que a venda foi concluída")
    nutricoes: List[Nutricao] = Field(default_factory=list, description="Lista de nutrições (interações) com o lead")
    procedimentos: List[Procedimento] = Field(default_factory=list, description="Lista de procedimentos de interesse do lead")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "cliente": {
                    "nome": "Maria Souza",
                    "telefone": ["11999998888"],
                    "email": ["maria.souza@example.com"],
                    "nascimento": "1985-08-20",
                    "origem": "Indicação"
                },
                "data_inicio": "2025-10-01T10:00:00",
                "data_venda": None,
                "nutricoes": [
                    {
                        "id": "nutri_xyz",
                        "acao": "Primeiro contato",
                        "data": "2025-10-01T10:00:00"
                    }
                ],
                "procedimentos": [
                    {
                        "id": "proc_67890",
                        "descricao": "Preenchimento Labial",
                        "referencia": "SKU-PRE-002",
                        "valor": "1800.00"
                    }
                ]
            }
        }
