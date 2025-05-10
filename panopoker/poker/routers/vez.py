from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from panopoker.core.database import get_db
from panopoker.poker.models.mesa import Mesa
from panopoker.poker.models.mesa import JogadorNaMesa
from panopoker.core.security import get_current_user
from panopoker.core.debug import debug_print

router = APIRouter(prefix="/mesa", tags=["Mesas"])

@router.get("/{mesa_id}/vez")
def buscar_vez(
    mesa_id: int,
    db: Session = Depends(get_db),
    current_user: JogadorNaMesa = Depends(get_current_user)
):
    mesa = db.query(Mesa).filter(Mesa.id == mesa_id).first()
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa não encontrada")

    debug_print(f"[DEBUG VEZ] Mesa {mesa.id} | Jogador da vez: {mesa.jogador_da_vez} | Estado: {mesa.estado_da_rodada}", silent=True)

    return {
        "jogador_da_vez_id": mesa.jogador_da_vez,
        "estado_da_rodada": mesa.estado_da_rodada,
    }
