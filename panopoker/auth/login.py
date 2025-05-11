from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from panopoker.core.database import get_db
from panopoker.usuarios.models.usuario import Usuario
from panopoker.core.security import create_access_token, verify_password
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from panopoker.core.config import GOOGLE_CLIENT_ID
from panopoker.core.debug import debug_print

router = APIRouter(prefix="/auth", tags=["Autenticação"])

class LoginRequest(BaseModel):
    nome: str | None = None
    password: str | None = None
    id_token: str | None = None

@router.post("/login")
def login_unificado(payload: LoginRequest, db: Session = Depends(get_db)):
    if payload.id_token:
        # === LOGIN COM GOOGLE ===
        try:
            idinfo = google_id_token.verify_oauth2_token(
                payload.id_token, google_requests.Request(), GOOGLE_CLIENT_ID
            )
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
        debug_print(f"[LOGIN] Login bem-sucedido para usuário {payload.nome} (ID {db_user.id})")

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "nome": db_user.nome,
            "user_id": db_user.id
        }
