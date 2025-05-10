from fastapi import APIRouter, Request, Depends
from starlette.responses import RedirectResponse
from panopoker.google.core import oauth
from sqlalchemy.orm import Session
from panopoker.core.database import get_db
from panopoker.usuarios.models.usuario import Usuario
from panopoker.core.security import create_access_token
from panopoker.google.core.oauth import google

router = APIRouter(prefix="/auth", tags=["Autenticação Google"])

@router.get("/login/google")
async def login_via_google(request: Request):
    redirect_uri = request.url_for("auth_callback")
    return await google.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    token = await google.authorize_access_token(request)
    user_info = await google.userinfo(token=token)

    email = user_info.get("email")
    nome = user_info.get("name")

    usuario = db.query(Usuario).filter_by(email=email).first()
    if not usuario:
        usuario = Usuario(
        nome=nome,
        email=email,
        senha_hash="google",
        auth_provider="google"
        )
        
        db.add(usuario)
        db.commit()
        db.refresh(usuario)

    jwt = create_access_token(data={"sub": usuario.nome})
    return {"access_token": jwt, "token_type": "bearer"}

