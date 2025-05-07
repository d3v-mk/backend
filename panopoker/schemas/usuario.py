from pydantic import BaseModel, EmailStr


class UserAuthenticated(BaseModel):
    email: EmailStr

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    nome: str
    email: EmailStr  # Usamos EmailStr para garantir que o e-mail seja válido

class UserCreate(UserBase):
    password: str  # Senha para o registro

class UserLogin(BaseModel):
    nome : str
    password: str

class User(UserBase):
    id: int
    saldo: float = 0.0  # Valor inicial de saldo do usuário

    class Config:
        from_attributes = True  # Isso permite que o Pydantic converta o modelo SQLAlchemy para Pydantic
