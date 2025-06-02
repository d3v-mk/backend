from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from panopoker.core.database import Base
from sqlalchemy import Column, Numeric, Boolean
from decimal import Decimal


class Promotor(Base):
    __tablename__ = "promotores"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, unique=True)
    usuario = relationship("Usuario", back_populates="promotor", lazy="joined")

    # ⚠️ ID da conta Mercado Pago
    user_id_mp = Column(String, unique=True, nullable=False)

    # ✅ Tokens do OAuth
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)

    slug = Column(String, unique=True, nullable=True)  # Será preenchido após o OAuth
    nome = Column(String, nullable=True)               # Pode ser definido depois
    avatar_url = Column(String, nullable=True)         # ✂️ Pode ser removido se virar obsoleto
    whatsapp = Column(String, nullable=True)

    saldo_repassar = Column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    comissao_total = Column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)

    bloqueado = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Promotor {self.nome or 'Sem nome'} | user_id={self.user_id}>"
