from sqlalchemy import Column, Integer, Float, ForeignKey, String, DateTime
from datetime import datetime
from panopoker.core.database import Base

class Saque(Base):
    __tablename__ = "saques"

    id = Column(Integer, primary_key=True)
    jogador_id = Column(Integer, ForeignKey("usuarios.id"))
    promotor_id = Column(Integer, ForeignKey("usuarios.id"))
    valor = Column(Float)
    status = Column(String, default="aguardando")  # 'aguardando', 'confirmado_pelo_jogador', 'concluido'
    criado_em = Column(DateTime, default=datetime.utcnow)
