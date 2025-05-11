from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from panopoker.core.config import settings
from panopoker.usuarios.models.usuario import Usuario
from sqlalchemy.orm import Session
from panopoker.core.database import SessionLocal, get_db



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# Função para criar um token JWT
def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=24)) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta  # Corrigido com timezone-aware
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt



# Função para obter o token de autorização (Bearer)
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sessão expirada ou inválida.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError, TypeError):
        raise credentials_exception

    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise credentials_exception  # 💥 Se o user não existe mais, rejeita o token

    return user



# Função para gerar o hash da senha
def hash_password(password: str) -> str:
    return pwd_context.hash(password)



# Função para verificar se a senha fornecida corresponde ao hash
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)