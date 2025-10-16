from pydantic import BaseModel, Field
from datetime import datetime

class Nutricao(BaseModel):
    """Modelo para representar uma nutrição (interação) com o lead."""
    id: str = Field(..., description="Identificador único da nutrição")
    acao: str = Field(..., description="Ação ou tipo de interação realizada")
    data: datetime = Field(..., description="Data e hora da nutrição")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "nutri_abcde",
                "acao": "Contato via WhatsApp",
                "data": "2025-10-15T14:30:00"
            }
        }
