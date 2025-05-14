from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from datetime import datetime
from panopoker.core.database import get_db
from panopoker.usuarios.models.usuario import Usuario
from panopoker.financeiro.models.saque import Saque
from panopoker.core.security import get_current_user
from pydantic import BaseModel

router = APIRouter(tags=["Saques"])

class ConfirmarSaqueRequest(BaseModel):
    valor_digitado: float

# Jogador confirma o saque
@router.post("/saques/{id}/confirmar")
def confirmar_saque(
    id: int,
    dados: ConfirmarSaqueRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    saque = db.query(Saque).filter(Saque.id == id).first()

    if not saque or saque.jogador_id != usuario.id:
        raise HTTPException(status_code=404, detail="Saque não encontrado")

    if saque.status != "aguardando":
        raise HTTPException(status_code=400, detail="Saque já confirmado")

    if round(dados.valor_digitado, 2) != round(saque.valor, 2):
        raise HTTPException(status_code=400, detail="Valor incorreto")

    if usuario.saldo < saque.valor:
        raise HTTPException(status_code=400, detail="Saldo insuficiente")

    usuario.saldo -= saque.valor
    saque.status = "confirmado_pelo_jogador"
    db.commit()

    return {"msg": "Saque confirmado"}


@router.get("/saques/me")
def meu_saque_pendente(db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    saque = db.query(Saque).filter(
        Saque.jogador_id == usuario.id,
        Saque.status == "aguardando"
    ).first()

    if not saque:
        raise HTTPException(status_code=404, detail="Nenhum saque pendente")

    return saque


