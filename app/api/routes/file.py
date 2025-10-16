from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/")
def home():
    return { "content": "Bem vindo ao anexo de arquivos" }