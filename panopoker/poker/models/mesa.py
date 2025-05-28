import enum
from sqlalchemy import (Column, Integer, Numeric, ForeignKey, Boolean, String)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON
from panopoker.core.database import Base
from sqlalchemy import BigInteger


class MesaStatus(str, enum.Enum):
    aberta = "aberta"
    em_jogo = "em_jogo"


class EstadoDaMesa:
    PRE_FLOP = "pre-flop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"
    SHOWDOWN = "showdown"


class Mesa(Base):
    __tablename__ = "mesas"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.cartas_comunitarias is None:
            print(f"⚠️ Mesa criada SEM cartas_comunitarias explícito: {kwargs}")
            self.cartas_comunitarias = {}
        elif isinstance(self.cartas_comunitarias, list):
            print(f"❌ Mesa criada com LISTA em cartas_comunitarias: {self.cartas_comunitarias}")
            self.cartas_comunitarias = {}

    id = Column(Integer, primary_key=True, index=True)
    rodada_id = Column(Integer, default=1)
    nome = Column(String, index=True)
    timestamp_inicio_rodada = Column(BigInteger, nullable=True)

    buy_in = Column(Numeric(10, 2), nullable=False)
    status = Column(String, default="aberta")

    limite_jogadores = Column(Integer, default=6)
    jogador_da_vez = Column(Integer, nullable=True)
    estado_da_rodada = Column(String, default="pre-flop")
    dealer_pos = Column(Integer, nullable=True)

    small_blind = Column(Numeric(10, 2), nullable=False)
    big_blind = Column(Numeric(10, 2), nullable=False)

    posicao_sb = Column(Integer, nullable=True)
    posicao_bb = Column(Integer, nullable=True)

    pote_total = Column(Numeric(10, 2), default=0.0)
    aposta_atual = Column(Numeric(10, 2), default=0.0)

    cartas_comunitarias = Column(JSON, default=dict)
    vencedores_ultima_rodada = Column(JSON, default=list)

    jogadores = relationship("JogadorNaMesa", back_populates="mesa", lazy="select")
    noticias = relationship("Noticia", back_populates="mesa", lazy="select")

    def __repr__(self):
        return f"<Mesa {self.id} - {self.nome} ({self.status})>"


class JogadorNaMesa(Base):
    __tablename__ = "jogadores_na_mesa"

    id = Column(Integer, primary_key=True, index=True)
    mesa_id = Column(Integer, ForeignKey("mesas.id", ondelete="CASCADE"), nullable=False)
    jogador_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)

    foldado = Column(Boolean, default=False)
    posicao_cadeira = Column(Integer, nullable=True)
    rodada_ja_agiu = Column(Boolean, default=False)
    participando_da_rodada = Column(Boolean, default=True)

    saldo_inicial = Column(Numeric(10, 2), nullable=False)
    saldo_atual = Column(Numeric(10, 2), nullable=False)

    aposta_atual = Column(Numeric(10, 2), default=0.0)
    aposta_acumulada = Column(Numeric(10, 2), default=0.0)

    cartas = Column(JSON, nullable=True, default=list)

    mesa = relationship("Mesa", back_populates="jogadores")
    jogador = relationship("Usuario", back_populates="mesas")

    def __repr__(self):
        return f"<JogadorNaMesa {self.jogador_id} - Mesa {self.mesa_id}>"
