from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from datetime import datetime
from panopoker.core.database import Base

class EstatisticasJogador(Base):
    __tablename__ = "estatisticas_jogador"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True)

    # Estatísticas padrão
    rodadas_ganhas = Column(Integer, default=0)
    fichas_ganhas = Column(Float, default=0.0)
    fichas_perdidas = Column(Float, default=0.0)
    flushes = Column(Integer, default=0)
    full_houses = Column(Integer, default=0)

    # Extras brabos
    sequencias = Column(Integer, default=0)
    quadras = Column(Integer, default=0)
    straight_flushes = Column(Integer, default=0)
    royal_flushes = Column(Integer, default=0)
    torneios_vencidos = Column(Integer, default=0)

    maior_pote = Column(Float, default=0.0)
    vitorias = Column(Integer, default=0)
    rodadas_jogadas = Column(Integer, default=0)
    mao_favorita = Column(String, nullable=True)  # Ex: "7C-7D"
    ranking_mensal = Column(Integer, nullable=True)
    vezes_no_top1 = Column(Integer, default=0)

    data_primeira_vitoria = Column(DateTime, nullable=True)
    data_ultima_vitoria = Column(DateTime, nullable=True)

    ultimo_update = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="estatisticas")
