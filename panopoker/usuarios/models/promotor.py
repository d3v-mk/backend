from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from panopoker.core.database import Base

class Promotor(Base):
    __tablename__ = "promotores"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True, unique=True)
    usuario = relationship("Usuario", back_populates="promotor")

    # ⚠️ Novo: ID da conta Mercado Pago
    user_id_mp = Column(String, unique=True, nullable=False)

    # ✅ Tokens do OAuth
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)

    slug = Column(String, unique=True, nullable=True)  # Será preenchido após o OAuth
    nome = Column(String, nullable=True)               # Pode ser definido depois
    avatar_url = Column(String, nullable=True)
