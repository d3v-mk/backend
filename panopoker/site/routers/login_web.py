from fastapi import APIRouter, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from panopoker.core.database import get_db
from panopoker.core.security import verify_password, create_access_token, get_current_user_optional
from panopoker.usuarios.models.usuario import Usuario
from panopoker.core.config import settings

router = APIRouter(prefix="/api")
IS_PRODUCTION = settings.IS_PRODUCTION

@router.post("/login-web")
def processar_login(
    username: str = Form(...),
    password: str = Form(...),
    next: str = Form("/"),
    db: Session = Depends(get_db),
):
    usuario = db.query(Usuario).filter(Usuario.nome == username).first()
    if not usuario or not verify_password(password, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="Usuário ou senha inválidos")

    token = create_access_token({"sub": str(usuario.id)})
    
    response = JSONResponse(content={"next": next})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=IS_PRODUCTION,
        samesite="None" if IS_PRODUCTION else "Lax",
        domain=".panopoker.com" if IS_PRODUCTION else None,
        path="/",
    )
    return response


@router.post("/logout")
def logout():
    response = JSONResponse({"message": "Logout realizado com sucesso"})
    response.delete_cookie(
        key="access_token",
        domain=".panopoker.com" if IS_PRODUCTION else None,
        path="/",
        secure=IS_PRODUCTION,
        samesite="None" if IS_PRODUCTION else "Lax",
    )
    return response

@router.get("/me")
def me(usuario: Usuario = Depends(get_current_user_optional)):
    if not usuario:
        raise HTTPException(status_code=401, detail="Não autenticado")

    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "is_admin": bool(usuario.is_admin),
        "is_promoter": bool(usuario.is_promoter),
        "avatar_url": usuario.avatar_url or f"https://i.pravatar.cc/150?u={usuario.nome}"
    }

