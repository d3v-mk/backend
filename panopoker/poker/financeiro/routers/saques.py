from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal, ROUND_DOWN, InvalidOperation
from panopoker.core.database import get_db
from panopoker.usuarios.models.usuario import Usuario
from panopoker.financeiro.models.saque import Saque
from panopoker.core.security import get_current_user
from pydantic import BaseModel

router = APIRouter(tags=["Saques"])

class ConfirmarSaqueRequest(BaseModel):
    valor_digitado: Decimal

def decimal2(val):
    # Função util pra padronizar duas casas
    try:
        return Decimal(val).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
    except (InvalidOperation, TypeError):
        raise HTTPException(status_code=400, detail="Valor inválido.")

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

    # Validação decimal, sempre 2 casas
    valor_digitado = decimal2(dados.valor_digitado)
    valor_saque = decimal2(saque.valor)

    if valor_digitado != valor_saque:
        raise HTTPException(status_code=400, detail="Valor incorreto")

    if decimal2(usuario.saldo) < valor_saque:
        raise HTTPException(status_code=400, detail="Saldo insuficiente")

    usuario.saldo = decimal2(usuario.saldo - valor_saque)
    saque.status = "confirmado_pelo_jogador"
    db.commit()

    return {"msg": "Saque confirmado"}

@router.get("/saques/me")
def meu_saque_pendente(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    saque = db.query(Saque).filter(
        Saque.jogador_id == usuario.id,
        Saque.status == "aguardando"
    ).first()

    if not saque:
        raise HTTPException(status_code=404, detail="Nenhum saque pendente")

    return saque
