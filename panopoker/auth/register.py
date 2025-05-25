from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from panopoker.usuarios.models.usuario import Usuario
from panopoker.schemas.usuario import UserCreate, User
from panopoker.core.database import get_db
from panopoker.core.security import hash_password
from panopoker.core.debug import debug_print
from panopoker.auth.utils.validadores_helper import verificar_email_valido, verificar_senha_forte

from panopoker.auth.utils.conq_beta_tester_helper import conq_beta_tester

router = APIRouter(prefix="/usuario", tags=["Usuario"])


# Endpoint para criar um novo usuário
@router.post("/register", response_model=User)
def registrar(user: UserCreate, db: Session = Depends(get_db)):
    debug_print(f"[REGISTRAR] Tentando registrar usuário {user.email}")

    # ⚠️ Verifica se o nome de usuário já existe
    if db.query(Usuario).filter(Usuario.nome == user.nome).first():
        raise HTTPException(status_code=400, detail="Nome de usuário já está em uso")

    # ⚠️ Verifica se o nome de usuário é muito curto
    if len(user.nome) < 6:
        raise HTTPException(status_code=400, detail="O nome de usuário deve ter pelo menos 6 caracteres.")

    # Verifica se o e-mail já existe no banco de dados
    db_user = db.query(Usuario).filter(Usuario.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Esse email já está em uso")

    # Verifica se a senha é forte
    verificar_senha_forte(user.password)

    # Verifica se o email é valido
    verificar_email_valido(user.email)

    # Criptografa a senha
    hashed_password = hash_password(user.password)

    # Cria o novo usuário
    db_user = Usuario(nome=user.nome, email=user.email, senha_hash=hashed_password)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    conq_beta_tester(db_user, db)

    return db_user
