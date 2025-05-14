from fastapi import APIRouter, Request, Form, Depends, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from panopoker.core.database import get_db
from panopoker.core.security import verify_password, create_access_token, get_current_user_optional
from panopoker.usuarios.models.usuario import Usuario
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import os

router = APIRouter(tags=["Painel Promotores"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "../templates"))

@router.get("/dashboard")
def dashboard_redirect(request: Request, usuario: Usuario = Depends(get_current_user_optional)):
    if not usuario:
        return RedirectResponse(url="/login", status_code=302)

    if not usuario.is_promoter:
        return RedirectResponse(url="/", status_code=302)

    return RedirectResponse(url="/painel/promotor", status_code=302)


@router.get("/login")
def exibir_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})



@router.post("/login-web")
def processar_login(request: Request, response: Response,
                    username: str = Form(...),
                    password: str = Form(...),
                    db: Session = Depends(get_db)):

    usuario = db.query(Usuario).filter(Usuario.nome == username).first()

    if not usuario or not verify_password(password, usuario.senha_hash):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "erro": "Usuário ou senha inválidos"
        })

    token = create_access_token({"sub": str(usuario.id)})
    resp = RedirectResponse(url="/dashboard", status_code=302)
    resp.set_cookie(
    key="access_token",
    value=token,
    httponly=True,
    secure=True,          # 🔒 obrigatório em HTTPS (ngrok é HTTPS)
    samesite="None"       # 🔁 permite redirecionamento entre domínios
    )
    return resp


@router.get("/logout")
def logout(response: Response):
    resp = RedirectResponse(url="/login", status_code=302)
    resp.delete_cookie("access_token")
    return resp