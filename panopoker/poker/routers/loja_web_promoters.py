from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from panopoker.core.database import get_db
from panopoker.usuarios.models.promotor import Promotor
from panopoker.usuarios.models.usuario import Usuario

router = APIRouter(prefix="/api", tags=["Loja"])

@router.get("/promotores-com-loja")
def listar_promotores_com_loja(db: Session = Depends(get_db)):
    promotores = (
        db.query(Promotor)
        .join(Usuario, Promotor.user_id == Usuario.id)
        .filter(Promotor.slug != None)
        .all()
    )
    return [
        {
            "id": p.id,
            "nome": p.usuario.nome,
            "slug": p.slug,
            "whatsapp": p.whatsapp,
            "avatarUrl": p.usuario.avatar_url
        }
        for p in promotores
    ]

