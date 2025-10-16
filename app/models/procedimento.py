from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

class Procedimento(BaseModel):
    """Modelo para representar um procedimento."""
    id: str = Field(..., description="Identificador único do procedimento")
    descricao: str = Field(..., description="Descrição do procedimento")
    referencia: Optional[str] = Field(None, description="Referência externa ou código do procedimento")
    valor: Decimal = Field(..., description="Valor do procedimento")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "proc_12345",
                "descricao": "Aplicação de Toxina Botulínica",
                "referencia": "SKU-TOX-001",
                "valor": "1200.50"
            }
        }
