from sqlalchemy import Column, Integer, String, Float, Boolean
from panopoker.core.database import Base
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy import DateTime, Column
from datetime import datetime, timezone



class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    id_publico = Column(String, unique=True, default=lambda: str(uuid.uuid4().int)[:8])
    data_registro = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    nome = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    senha_hash = Column(String)
    saldo = Column(Float, default=0.0)
    is_admin = Column(Boolean, default=False)
    is_promoter = Column(Boolean, default=False)
    avatar_url = Column(String)
    
    auth_provider = Column(String, default="local") # Identifica se foi registrado localmente ou com o google


    #Relationships
    mesas = relationship("JogadorNaMesa", back_populates="jogador")  # Relacionamento com mesas
    pagamentos = relationship("Pagamento", back_populates="user") # Relacionamento com pagamento
    promotor = relationship("Promotor", back_populates="usuario", uselist=False)
    estatisticas = relationship("EstatisticasJogador", back_populates="usuario", uselist=False)
    noticias = relationship("Noticia", back_populates="usuario", lazy="select")


    def __repr__(self):
        return f"<Usuario {self.id} - {self.nome}>"


# Late Lazy import
from panopoker.usuarios.models.promotor import Promotor
from .estatisticas import EstatisticasJogador
from panopoker.lobby.models.noticias import Noticia