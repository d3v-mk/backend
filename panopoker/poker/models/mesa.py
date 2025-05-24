import enum
from sqlalchemy import Column, Integer, Float, ForeignKey, Boolean, String
from sqlalchemy.orm import relationship
from panopoker.core.database import Base
from sqlalchemy.dialects.postgresql import JSON


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


    id = Column(Integer, primary_key=True, index=True) # ID da mesa
    rodada_id = Column(Integer, default=1) # Identifica a rodada
    nome = Column(String, index=True) # Nome da mesa
    buy_in = Column(Float)  # Valor mínimo da mesa (buy-in)
    status = Column(String, default="aberta")  # Status da mesa ('aberta', 'em_jogo', 'fechada')
    limite_jogadores = Column(Integer, default=6)  # Limite máximo de jogadores
    jogador_da_vez = Column(Integer, nullable=True) # Identifica a vez do jogador jogar
    estado_da_rodada = Column(String, default="pre-flop") # Estado da rodada atual da mesa
    dealer_pos = Column(Integer, nullable=True) # Posicao do dealer
    small_blind = Column(Float)  # Valor do small blind
    big_blind = Column(Float)  # Valor do big blind
    posicao_sb = Column(Integer, nullable=True)
    posicao_bb = Column(Integer, nullable=True)


    pote_total = Column(Float, default=0.0) # Pote total da mesa
    aposta_atual = Column(Float, default=0.0) # Aposta atual na mesa


    cartas_comunitarias = Column(JSON, default=dict) # Mostrar cartas comunitarias
    vencedores_ultima_rodada = Column(JSON, default=[]) #INUTIL POR ENQUANTO <------


    jogadores = relationship("JogadorNaMesa", back_populates="mesa", lazy="select")

    noticias = relationship("Noticia", back_populates="mesa", lazy="select")

    def __repr__(self):
        return f"<Mesa {self.id} - {self.nome} ({self.status})>"
    


class JogadorNaMesa(Base):
    __tablename__ = "jogadores_na_mesa"

    id = Column(Integer, primary_key=True, index=True) # id do registro JogadorNaMesa (único pra cada entrada)
    mesa_id = Column(Integer, ForeignKey("mesas.id")) # em qual mesa ele tá
    jogador_id = Column(Integer, ForeignKey("usuarios.id"))  # Referência para o usuário (jogador)
    foldado = Column(Boolean, default=False)  # 0 = não, 1 = sim (se o jogador deu fold)

    posicao_cadeira = Column(Integer, nullable=True) # Posicao do jogador sentado na cadeira
    rodada_ja_agiu = Column(Boolean, default=False) # Verifica se o jogador ja agiu naquela rodada
    participando_da_rodada = Column(Boolean, default=True) # Verifica jogador participando da rodada


    saldo_inicial = Column(Float)  # O saldo do jogador ao entrar na mesa
    saldo_atual = Column(Float)  # O saldo atual do jogador (deve ser atualizado conforme as apostas)
    
    aposta_atual = Column(Float, default=0.0)  # A aposta atual do jogador na rodada
    aposta_acumulada = Column(Float, default=0.0) # Aposta acumulada de todos os jogadores

 
    cartas = Column(JSON, nullable=True, default=[]) # Cartas do jogador na mesa

    mesa = relationship("Mesa", back_populates="jogadores")
    jogador = relationship("Usuario", back_populates="mesas")

    def __repr__(self):
        return f"<JogadorNaMesa {self.jogador_id} - {self.mesa_id}>"