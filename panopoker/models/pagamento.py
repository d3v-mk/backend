from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from panopoker.core.database import Base

class Pagamento(Base):
    __tablename__ = "pagamentos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"))
    valor = Column(Float, nullable=False)
    status = Column(String, default="pending")
    payment_id = Column(String, unique=True)
    qr_code = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("Usuario", back_populates="pagamentos")
