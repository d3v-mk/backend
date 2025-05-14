from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from panopoker.core.database import get_db
from panopoker.usuarios.models.usuario import Usuario
from panopoker.core.security import create_access_token, verify_password
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from panopoker.core.debug import debug_print
import httpx
from fastapi.responses import RedirectResponse
from panopoker.core.config import GOOGLE_ANDROID_CLIENT_ID, GOOGLE_WEB_CLIENT_ID, GOOGLE_WEB_CLIENT_SECRET

router = APIRouter(prefix="/auth", tags=["Autenticação"])

class LoginRequest(BaseModel):
    nome: str | None = None
    password: str | None = None
    id_token: str | None = None


# === LOGIN DO APP ===
@router.post("/login")
def login_unificado(payload: LoginRequest, db: Session = Depends(get_db)):
    if payload.id_token:
        # === LOGIN COM GOOGLE ===
        try:
            idinfo = google_id_token.verify_oauth2_token(
                payload.id_token, google_requests.Request()
            )

            aud = idinfo.get("aud")
            if aud not in [GOOGLE_ANDROID_CLIENT_ID, GOOGLE_WEB_CLIENT_ID]:
                raise HTTPException(status_code=401, detail="Client ID inválido")

            email = idinfo.get("email")
            nome = idinfo.get("name")

        except Exception as e:
            raise HTTPException(status_code=401, detail="Token inválido ou expirado")


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

        jwt_token = create_access_token(data={"sub": str(usuario.id)})
        return {
            "access_token": jwt_token,
            "token_type": "bearer",
            "nome": usuario.nome,
            "user_id": usuario.id
        }

    else:
        # === LOGIN COM USUÁRIO E SENHA ===
        if not payload.nome or not payload.password:
            raise HTTPException(status_code=400, detail="Credenciais ausentes")

        debug_print(f"[LOGIN] Tentativa de login para usuário {payload.nome}")
        db_user = db.query(Usuario).filter(Usuario.nome == payload.nome).first()

        if db_user is None:
            debug_print(f"[LOGIN][ERRO] Usuário {payload.nome} não encontrado")
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if db_user.auth_provider == "google":
            raise HTTPException(status_code=400, detail="Use o login com Google.")

        if not verify_password(payload.password, db_user.senha_hash):
            debug_print(f"[LOGIN][ERRO] Senha inválida para usuário {payload.nome}")
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = create_access_token(data={"sub": str(db_user.id)})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "nome": db_user.nome,
            "user_id": db_user.id
        }
    

# === LOGIN DOS PROMOTRES HTML WEB ===
from fastapi.responses import RedirectResponse

@router.get("/callback-web")
def google_callback_web(request: Request, db: Session = Depends(get_db)):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Código ausente")

    token_url = "https://oauth2.googleapis.com/token"
    redirect_uri = "http://localhost:8000/auth/callback-web"

    data = {
        "code": code,
        "client_id": GOOGLE_WEB_CLIENT_ID,
        "client_secret": GOOGLE_WEB_CLIENT_SECRET,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }

    response = httpx.post(token_url, data=data)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Falha ao obter token")

    tokens = response.json()
    id_token = tokens.get("id_token")
    if not id_token:
        raise HTTPException(status_code=400, detail="Token não recebido")

    login_payload = LoginRequest(id_token=id_token)
    resultado = login_unificado(login_payload, db)
    access_token = resultado["access_token"]

    # ✅ Redireciona e salva o token em cookie
    resp = RedirectResponse(url="/dashboard", status_code=302)
    resp.set_cookie(key="access_token", value=access_token, httponly=True)
    return resp

