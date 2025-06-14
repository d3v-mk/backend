from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from panopoker.core.database import get_db
from panopoker.usuarios.models.usuario import Usuario
from panopoker.usuarios.models.promotor import Promotor
from jose import jwt, JWTError
from panopoker.core.config import settings

router = APIRouter(prefix="/api")

def get_current_user_cookie(request: Request, db: Session = Depends(get_db)) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sessão expirada ou inválida.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = request.cookies.get("access_token")
    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError, TypeError):
        raise credentials_exception

    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise credentials_exception

    return user

@router.get("/admin/promotor/listar")
def listar_promotores(
    ativo: str = Query("todos", pattern="^(todos|ativos|bloqueados)$"),
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_current_user_cookie)
):
    if not admin.is_admin:
        raise HTTPException(status_code=403, detail="Acesso não autorizado")

    query = db.query(Promotor)

    if ativo == "ativos":
        query = query.filter(Promotor.bloqueado == False)
    elif ativo == "bloqueados":
        query = query.filter(Promotor.bloqueado == True)

    promotores = query.all()

    return [
        {
            "id": p.id,
            "user_id": p.user_id,
            "user_id_mp": p.user_id_mp,
            "nome": p.nome,
            "slug": p.slug,
            "access_token": p.access_token,
            "saldo": float(p.saldo_repassar),
            "bloqueado": p.bloqueado,
            #"ultima_atividade": str(p.usuario.ultima_atividade) if p.usuario and p.usuario.ultima_atividade else None,
        }
        for p in promotores
    ]
