from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from panopoker.core.database import get_db
from panopoker.usuarios.models.usuario import Usuario
from panopoker.usuarios.models.promotor import Promotor
from panopoker.core.security import get_current_user_optional
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["Admin"])

templates = Jinja2Templates(directory="panopoker/site/templates")


@router.get("/painel/admin", response_class=HTMLResponse)
def painel_admin_promotores(
    request: Request,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_current_user_optional)
):
    if not admin:
        return RedirectResponse(url="/login", status_code=302)

    if not admin.is_admin:
        return HTMLResponse("<h1>Acesso não autorizado</h1>", status_code=403)

    promotores = db.query(Promotor).all()

    return templates.TemplateResponse("painel_admin.html", {
        "request": request,
        "promotores": promotores
    })

@router.get("/painel/dev", response_class=HTMLResponse)
def painel_dev(
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user_optional)
):
    if not usuario:
        return RedirectResponse(url="/login", status_code=302)

    # Se quiser restringir só para admins, descomenta abaixo
    if not usuario.is_admin:
        return HTMLResponse("<h1>Acesso não autorizado</h1>", status_code=403)

    # Pode mandar dados extras pro template se quiser
    # tipo tokens, mesa default, etc — mas se for só front, pode ser vazio
    return templates.TemplateResponse("painel_dev.html", {
        "request": request,
        "usuario": usuario,
    })

