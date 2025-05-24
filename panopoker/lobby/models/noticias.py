import enum
from datetime import datetime
from sqlalchemy import Column, Integer, Float, ForeignKey, Boolean, String, DateTime
from sqlalchemy.orm import relationship
from panopoker.core.database import Base

class Noticia(Base):
    __tablename__ = "noticias"
    
    id = Column(Integer, primary_key=True, index=True)
    mensagem = Column(String, nullable=False)
    tipo = Column(String, default="noticia")  # "noticia", "evento", "admin", etc
    criada_em = Column(DateTime, default=datetime.utcnow)
    mesa_id = Column(Integer, ForeignKey("mesas.id"), nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    # Relationships (opcionais, mas úteis se quiser acessar dados direto pelo objeto)
    mesa = relationship("Mesa", back_populates="noticias", lazy="joined")
    usuario = relationship("Usuario", back_populates="noticias", lazy="joined")

    def __repr__(self):
        return f"<Noticia {self.id} | {self.tipo} | {self.mensagem[:30]}...>"
