from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from panopoker.core.database import get_db
from fastapi import Depends
from fastapi.templating import Jinja2Templates
from panopoker.usuarios.models.usuario import Usuario
from panopoker.usuarios.models.promotor import Promotor
from sqlalchemy.orm import joinedload
from time import time
import requests

router = APIRouter(tags=["Loja Promotores"])
templates = Jinja2Templates(directory="panopoker/site/templates")


# ============================= LINK DA LOJA DO PROMOTOR =============================

@router.get("/loja/promotor/{slug}", response_class=HTMLResponse)
def loja_promotor(slug: str, request: Request, db: Session = Depends(get_db)):
    promotor = db.query(Promotor)\
        .options(joinedload(Promotor.usuario))\
        .filter(Promotor.slug == slug).first()
    
    if not promotor:
        return HTMLResponse(
            content="<h1>Olá jogador!</h1><h1>Loja não encontrada</h1><h1>Verifique se o link está correto.</h1>",
            status_code=404
        )

    return templates.TemplateResponse("loja_promotor.html", {
        "request": request,
        "nome": promotor.nome,
        "slug": promotor.slug,
        "avatar_url": promotor.usuario.avatar_url if promotor.usuario else "",
        "timestamp": int(time()),
        # Nada de pix_copias aqui
    })


