from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from panopoker.core.database import get_db
from panopoker.core.security import get_current_user_optional
from panopoker.usuarios.models.usuario import Usuario
from panopoker.usuarios.models.promotor import Promotor
from panopoker.financeiro.models.saque import Saque
from decimal import Decimal
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

@router.get("/promotor/saques")
def listar_saques_promotor(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user_optional)
):
    if usuario is None or not usuario.is_promoter:
        return {"erro": "Não autorizado"}

    saques = db.query(Saque).options(joinedload(Saque.jogador)).filter(
        Saque.promotor_id == usuario.id
    ).order_by(Saque.criado_em.desc()).all()

    resultado = []
    for saque in saques:
        resultado.append({
            "id": saque.id,
            "valor": str(saque.valor),
            "status": saque.status,
            "criado_em": saque.criado_em.isoformat() if saque.criado_em else None,
            "jogador": {
                "id": saque.jogador.id,
                "nome": saque.jogador.nome,
                "id_publico": saque.jogador.id_publico,
            }
        })

    return {"saques": resultado}




class SolicitarSaquePayload(BaseModel):
    id_publico: str
    valor: str  # mantido como string pra garantir precisão

@router.post("/painel/promotor/solicitar_saque")
def solicitar_saque_api(
    payload: SolicitarSaquePayload,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user_optional)
):
    if not usuario or not usuario.is_promoter:
        raise HTTPException(status_code=401, detail="Não autorizado")

    jogador = db.query(Usuario).filter(Usuario.id_publico == payload.id_publico).first()
    if not jogador:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")

    saque = Saque(
        jogador_id=jogador.id,
        promotor_id=usuario.id,
        valor=Decimal(payload.valor),
        status="aguardando",
        criado_em=datetime.utcnow()
    )
    db.add(saque)
    db.commit()
    return {"msg": "Saque solicitado com sucesso"}
