from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from panopoker.core.database import get_db
from panopoker.lobby.models.noticias import Noticia

router = APIRouter(prefix="/lobby", tags=["Lobby"])

@router.get("/noticias/admin")
def listar_noticias_admin(limit: int = 1, db: Session = Depends(get_db)):
    noticias = (
        db.query(Noticia)
        .filter(Noticia.tipo == "admin")
        .order_by(Noticia.criada_em.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": n.id,
            "mensagem": n.mensagem,
            "tipo": n.tipo,
            "criada_em": n.criada_em.isoformat(),
            "mesa_id": n.mesa_id,
            "usuario_id": n.usuario_id,
        }
        for n in noticias
    ]


@router.get("/noticias")
def listar_noticias(
    limit: int = 1,
    db: Session = Depends(get_db)
):
    noticias = (
        db.query(Noticia)
        .filter(Noticia.tipo != "admin") 
        .order_by(Noticia.criada_em.desc())
        .limit(limit)
        .all()
    )
    return [ 
        {
            "id": n.id,
            "mensagem": n.mensagem,
            "tipo": n.tipo,
            "criada_em": n.criada_em.isoformat(),
            "mesa_id": n.mesa_id,
            "usuario_id": n.usuario_id,
        }
        for n in noticias
    ]


