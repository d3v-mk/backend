from sqlalchemy import Column, Integer, String, Float, Boolean
from panopoker.core.database import Base
from sqlalchemy.orm import relationship

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    senha_hash = Column(String)
    saldo = Column(Float, default=0.0)
    is_admin = Column(Boolean, default=False)

    mesas = relationship("JogadorNaMesa", back_populates="jogador")  # Relacionamento com mesas

    pagamentos = relationship("Pagamento", back_populates="user") # Relacionamento com pagamento

    def __repr__(self):
        return f"<Usuario {self.id} - {self.nome}>"
