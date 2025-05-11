from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from panopoker.usuarios.models.usuario import Usuario
from panopoker.schemas.usuario import UserCreate, User, UserLogin
from panopoker.core.database import get_db
from panopoker.core.security import hash_password, verify_password, create_access_token, get_current_user
from datetime import timedelta
from panopoker.core.debug import debug_print

router = APIRouter(prefix="/usuario", tags=["Usuario"])


@router.get("/saldo")
def get_user_balance(
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user)
):
    return {"saldo": user.saldo}


@router.get("/{id}")
def get_usuario_por_id(id: int, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    usuario = db.query(Usuario).filter(Usuario.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"id": usuario.id, "nome": usuario.nome, "email": usuario.email}

