from sqlalchemy import Column, Integer, Numeric, ForeignKey, String, DateTime 
from datetime import datetime
from panopoker.core.database import Base
from sqlalchemy.orm import relationship
import uuid

class Saque(Base):
    __tablename__ = "saques"

    id = Column(Integer, primary_key=True)
    jogador_id = Column(Integer, ForeignKey("usuarios.id"))
    promotor_id = Column(Integer, ForeignKey("usuarios.id"))
    valor = Column(Numeric(10, 2), nullable=False)  # 👈 Troca aqui: Numeric(10,2) é padrão para dinheiro!
    status = Column(String, default="aguardando")  # 'aguardando', 'confirmado_pelo_jogador', 'concluido'
    criado_em = Column(DateTime(timezone=True), default=datetime.utcnow)

    saque_id_publico = Column(String, unique=True, default=lambda: str(uuid.uuid4())[:8].upper())

    jogador = relationship("Usuario", foreign_keys=[jogador_id])
    promotor = relationship("Usuario", foreign_keys=[promotor_id])

    def __repr__(self):
        return f"<Saque {self.saque_id_publico} | R${self.valor:.2f} | {self.status}>"
