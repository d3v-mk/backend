from fastapi import APIRouter, Request, Form, Depends, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from panopoker.core.database import get_db
from panopoker.core.security import verify_password, create_access_token, get_current_user_optional
from panopoker.usuarios.models.usuario import Usuario
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from panopoker.core.config import settings
import os

router = APIRouter(tags=[""])

IS_PRODUCTION = settings.IS_PRODUCTION
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "../templates"))

@router.get("/dashboard")
def dashboard_redirect(request: Request, usuario: Usuario = Depends(get_current_user_optional)):
    if not usuario:
        return RedirectResponse(url="/login", status_code=302)

    if usuario.is_admin:
        return RedirectResponse(url="/painel/admin", status_code=302)

    if usuario.is_promoter:
        return RedirectResponse(url="/painel/promotor", status_code=302)

    return RedirectResponse(url="/", status_code=302)



@router.get("/login")
def exibir_login(request: Request, next: str | None = None):
    return templates.TemplateResponse("login.html", {
        "request": request,
        "next": next,
        "google_redirect_uri_web_final": settings.GOOGLE_REDIRECT_URI_WEB_FINAL,
        "google_client_id": settings.GOOGLE_WEB_CLIENT_ID
    })


@router.get("/finaliza_login")
def finaliza_login(request: Request):
    return templates.TemplateResponse("finaliza_login.html", {"request": request})



@router.post("/login-web")
def processar_login(request: Request, response: Response,
                    username: str = Form(...),
                    password: str = Form(...),
                    next: str = Form("/"),
                    db: Session = Depends(get_db)):

    usuario = db.query(Usuario).filter(Usuario.nome == username).first()

    if not usuario or not verify_password(password, usuario.senha_hash):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "erro": "Usuário ou senha inválidos",
            "next": next
        })

    token = create_access_token({"sub": str(usuario.id)})
    resp = RedirectResponse(url=next, status_code=302)
    resp.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=IS_PRODUCTION,
        samesite="None" if IS_PRODUCTION else "Lax",
        domain=".panopoker.com" if IS_PRODUCTION else None
    )
    return resp


@router.get("/logout")
def logout(response: Response):
    resp = RedirectResponse(url="/login", status_code=302)
    resp.delete_cookie(
        key="access_token",
        domain=".panopoker.com" if settings.IS_PRODUCTION else None,
        path="/",
        secure=settings.IS_PRODUCTION,
        samesite="None" if settings.IS_PRODUCTION else "Lax",
    )
    return resp
