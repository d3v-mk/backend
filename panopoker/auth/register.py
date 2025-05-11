from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from panopoker.usuarios.models.usuario import Usuario
from panopoker.schemas.usuario import UserCreate, User, UserLogin
from panopoker.core.database import get_db
from panopoker.core.security import hash_password, verify_password, create_access_token, get_current_user
from datetime import timedelta
from panopoker.core.debug import debug_print

router = APIRouter(prefix="/usuario", tags=["Usuario"])


# Endpoint para criar um novo usuário
@router.post("/register", response_model=User)
def registrar(user: UserCreate, db: Session = Depends(get_db)):
    debug_print(f"[REGISTRAR] Tentando registrar usuário {user.email}")

    # Verifica se o e-mail já existe no banco de dados
    db_user = db.query(Usuario).filter(Usuario.email == user.email).first()
    if db_user:
        debug_print(f"[REGISTRAR][ERRO] Email {user.email} já está em uso")
        raise HTTPException(status_code=400, detail="Esse email já está em uso")

    # Criptografa a senha
    hashed_password = hash_password(user.password)
    debug_print(f"[REGISTRAR] Senha do usuário {user.email} criptografada")

    # Cria um novo usuário
    db_user = Usuario(nome=user.nome, email=user.email, senha_hash=hashed_password)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    debug_print(f"[REGISTRAR] Usuário {user.email} registrado com sucesso (ID {db_user.id})")

    return db_user
