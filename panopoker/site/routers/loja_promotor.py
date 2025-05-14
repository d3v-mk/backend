from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from panopoker.core.database import get_db
from fastapi import Depends
from fastapi.templating import Jinja2Templates
from panopoker.usuarios.models.usuario import Usuario
from panopoker.usuarios.models.promotor import Promotor
import requests

router = APIRouter(tags=["Loja Promotores"])
templates = Jinja2Templates(directory="panopoker/site/templates")


# ============================= LINK DA LOJA DO PROMOTOR =============================

@router.get("/loja/{slug}", response_class=HTMLResponse)
def loja_promotor(slug: str, request: Request, db: Session = Depends(get_db)):
    promotor = db.query(Promotor).filter(Promotor.slug == slug).first()
    if not promotor:
        raise HTTPException(status_code=404, detail="Promotor não encontrado")

    return templates.TemplateResponse("loja_promotor.html", {
        "request": request,
        "nome": promotor.nome,
        "slug": promotor.slug,
        "avatar_url": promotor.avatar_url
        # Nada de pix_copias aqui
    })


