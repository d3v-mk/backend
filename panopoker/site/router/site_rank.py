from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from panopoker.core.database import get_db
from panopoker.usuarios.models.estatisticas import EstatisticasJogador
from panopoker.usuarios.models.usuario import Usuario

router = APIRouter(prefix="/api")

@router.get("/ranking/geral")
def get_ranking_geral(db: Session = Depends(get_db), limit: int = 10, offset: int = 0):
    jogadores = (
        db.query(EstatisticasJogador)
        .options(joinedload(EstatisticasJogador.usuario))
        .order_by(EstatisticasJogador.vitorias.desc(), EstatisticasJogador.rodadas_jogadas.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )

    ranking = []
    for estats in jogadores:
        usuario = estats.usuario
        if usuario:
            ranking.append({
                "usuario_id": usuario.id,
                "nome": usuario.nome,
                "avatar_url": usuario.avatar_url,
                "vitorias": estats.vitorias,
                "rodadas_jogadas": estats.rodadas_jogadas,
                # Exemplo de extra
                "porcentagem_vitorias": round((estats.vitorias / estats.rodadas_jogadas) * 100, 1) if estats.rodadas_jogadas else 0.0
            })

    return {"ranking": ranking}
