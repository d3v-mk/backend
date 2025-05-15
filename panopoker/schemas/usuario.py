from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

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


class PerfilResponse(BaseModel):
    id_publico: str
    nome: str
    avatar_url: Optional[str]

    # Estatísticas principais
    rodadas_ganhas: int
    fichas_ganhas: float
    fichas_perdidas: float
    flushes: int
    full_houses: int

    # Extras lendários
    sequencias: int
    quadras: int
    straight_flushes: int
    royal_flushes: int
    torneios_vencidos: int

    maior_pote: float
    vitorias: int
    rodadas_jogadas: int
    mao_favorita: Optional[str]
    ranking_mensal: Optional[int]
    vezes_no_top1: int
    data_primeira_vitoria: Optional[datetime]
    data_ultima_vitoria: Optional[datetime]
    ultimo_update: Optional[datetime]