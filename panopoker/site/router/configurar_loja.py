from fastapi import Request, Depends, HTTPException, APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from panopoker.core.security import get_current_user_optional
from sqlalchemy.orm import Session
from panopoker.core.database import get_db
from panopoker.usuarios.models.usuario import Usuario
from panopoker.usuarios.models.promotor import Promotor
from fastapi import Form


templates = Jinja2Templates(directory="panopoker/site/templates")

router = APIRouter(prefix="/api")

@router.get("/loja/configurar", response_class=HTMLResponse)
def configurar_loja(
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user_optional)
):
    # Verifica se o usuário está logado
    if not usuario:
        raise HTTPException(status_code=401, detail="Você precisa estar logado para acessar.")

    # Verifica se é promotor
    if not usuario.is_promoter:
        raise HTTPException(status_code=403, detail="Apenas promotores podem configurar loja.")

    # Busca o promotor pelo user_id
    promotor = db.query(Promotor).filter(Promotor.user_id == usuario.id).first()
    if not promotor:
        raise HTTPException(status_code=404, detail="Promotor não encontrado.")

    # Renderiza o template com os dados atuais
    return templates.TemplateResponse("configurar_loja.html", {
        "request": request,
        "slug_atual": promotor.slug or "",
        "whatsapp": promotor.whatsapp or "",
        "nome": promotor.nome or usuario.nome or "",
    })




@router.post("/loja/configurar")
def salvar_config_loja(
    slug: str = Form(...),
    whatsapp: str = Form(...),
    nome: str = Form(""),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user_optional)
):
    promotor = db.query(Promotor).filter(Promotor.user_id == usuario.id).first()
    if not promotor:
        raise HTTPException(status_code=404, detail="Usuário não é promotor.")


    # Verifica se o slug já existe em outro promotor
    slug_existente = db.query(Promotor).filter(Promotor.slug == slug, Promotor.id != promotor.id).first()
    if slug_existente:
        raise HTTPException(status_code=400, detail="Esse slug já está em uso por outro promotor.")

    promotor.slug = slug
    promotor.whatsapp = whatsapp
    promotor.nome = nome or promotor.nome
    db.commit()

    return RedirectResponse(url=f"/loja/promotor/{slug}", status_code=302)
