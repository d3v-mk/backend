from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from panopoker.core.database import get_db
from panopoker.models.mesa import Mesa

router = APIRouter(prefix="/mesa", tags=["Mesas"])

@router.get("/abertas")
def listar_mesas_abertas(db: Session = Depends(get_db)):
    todas_mesas = db.query(Mesa).all()

    if not todas_mesas:
        raise HTTPException(status_code=404, detail="Nenhuma mesa aberta disponível")

    return [
        {
            "id": mesa.id,
            "nome": mesa.nome,
            "buy_in": mesa.buy_in,
            "status": mesa.status,
            "limite_jogadores": mesa.limite_jogadores,
            "jogadores_atuais": len(mesa.jogadores),
            "tipo_jogo": "Texas Hold'em",  # pode deixar fixo
        }
        for mesa in todas_mesas
    ]
