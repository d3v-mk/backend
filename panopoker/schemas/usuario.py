from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from decimal import Decimal

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
    saldo: Decimal = Decimal("0.00")  # Valor inicial de saldo do usuário

    class Config:
        from_attributes = True  # Isso permite que o Pydantic converta o modelo SQLAlchemy para Pydantic


class NoticiaAdminCreate(BaseModel):
    mensagem: str

class PerfilResponse(BaseModel):
    id_publico: str
    nome: str
    avatar_url: Optional[str]
    is_promoter: bool = False

    # Estatísticas principais
    rodadas_ganhas: int
    fichas_ganhas: Decimal
    fichas_perdidas: Decimal
    flushes: int
    full_houses: int

    # Extras lendários
    sequencias: int
    quadras: int
    straight_flushes: int
    royal_flushes: int
    torneios_vencidos: int

    maior_pote: Decimal
    vitorias: int
    rodadas_jogadas: int
    mao_favorita: Optional[str]
    ranking_mensal: Optional[int]
    vezes_no_top1: int
    data_primeira_vitoria: Optional[datetime]
    data_ultima_vitoria: Optional[datetime]
    ultimo_update: Optional[datetime]

    # Conquistas
    beta_tester: Optional[int] = 0
