from fastapi import Request, Depends, HTTPException, APIRouter
from panopoker.core.security import get_current_user_optional
from sqlalchemy.orm import Session
from panopoker.core.database import get_db
from panopoker.usuarios.models.usuario import Usuario
from panopoker.usuarios.models.promotor import Promotor
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api")

@router.get("/loja/configurar")
def configurar_loja(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user_optional)
):
    if not usuario:
        raise HTTPException(status_code=401, detail="Você precisa estar logado para acessar.")

    if not usuario.is_promoter:
        raise HTTPException(status_code=403, detail="Apenas promotores podem configurar loja.")

    promotor = db.query(Promotor).filter(Promotor.user_id == usuario.id).first()
    if not promotor:
        raise HTTPException(status_code=404, detail="Promotor não encontrado.")

    return {
        "slug_atual": promotor.slug or "",
        "whatsapp": promotor.whatsapp or "",
        "nome": promotor.nome or usuario.nome or ""
    }


from pydantic import BaseModel

class LojaConfigPayload(BaseModel):
    slug: str
    whatsapp: str
    nome: str = ""

@router.post("/loja/configurar")
def salvar_config_loja(
    payload: LojaConfigPayload,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user_optional)
):
    if not usuario:
        raise HTTPException(status_code=401, detail="Você precisa estar logado.")

    promotor = db.query(Promotor).filter(Promotor.user_id == usuario.id).first()
    if not promotor:
        raise HTTPException(status_code=404, detail="Usuário não é promotor.")

    # Verifica se slug já existe em outro promotor
    slug_existente = db.query(Promotor).filter(
        Promotor.slug == payload.slug,
        Promotor.id != promotor.id
    ).first()
    if slug_existente:
        raise HTTPException(status_code=400, detail="Esse slug já está em uso por outro promotor.")

    promotor.slug = payload.slug
    promotor.whatsapp = payload.whatsapp
    promotor.nome = payload.nome or promotor.nome
    db.commit()

    return {"message": "Configuração salva com sucesso!", "slug": promotor.slug}
