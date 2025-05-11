from sqlalchemy.orm import Session
from panopoker.core.database import SessionLocal
from panopoker.usuarios.models.usuario import Usuario
from passlib.context import CryptContext
from panopoker.poker.models.mesa import JogadorNaMesa



# PYTHONPATH=. python3 panopoker/tests/add_usuario.py

db: Session = SessionLocal()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

senha_hash = pwd_context.hash("123")  # Gera hash da senha

# Dados dos usuários
usuarios = [
    {"nome": "mk0", "email": "mk21@panopoker.com"},
    {"nome": "mk1", "email": "mk1@panopoker.com"},
    {"nome": "mk2", "email": "mk2@panopoker.com"},
    {"nome": "mk3", "email": "mk3@panopoker.com"},
    {"nome": "mk4", "email": "mk4@panopoker.com"},
    {"nome": "mk5", "email": "mk5@panopoker.com"},
]

# Criação no banco
for u in usuarios:
    novo_usuario = Usuario(
        nome=u["nome"],
        email=u["email"],
        senha_hash=senha_hash,
        saldo=100.0
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

print(f"✅ Usuários criados")
