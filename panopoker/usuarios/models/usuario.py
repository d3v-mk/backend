from sqlalchemy import Column, Integer, String, Boolean, DateTime, DECIMAL
from sqlalchemy.orm import relationship
from panopoker.core.database import Base
from datetime import datetime, timezone
import uuid

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    id_publico = Column(String, unique=True, default=lambda: str(uuid.uuid4().int)[:8])
    data_registro = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    nome = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)

    saldo = Column(DECIMAL(10, 2), default=0.00)
    is_admin = Column(Boolean, default=False)
    is_promoter = Column(Boolean, default=False)
    avatar_url = Column(String, nullable=True)

    visitas_ao_site = Column(Integer, default=0)

    auth_provider = Column(String, default="local")

    # Relationships
    mesas = relationship("JogadorNaMesa", back_populates="jogador", lazy="select")
    pagamentos = relationship("Pagamento", back_populates="user", lazy="select")
    promotor = relationship("Promotor", back_populates="usuario", uselist=False, lazy="joined")
    estatisticas = relationship("EstatisticasJogador", back_populates="usuario", uselist=False, lazy="joined")
    noticias = relationship("Noticia", back_populates="usuario", lazy="select")

    def __repr__(self):
        return f"<Usuario {self.id} - {self.nome}>"



# Late Lazy import
from panopoker.usuarios.models.promotor import Promotor
from .estatisticas import EstatisticasJogador
from panopoker.lobby.models.noticias import Noticia