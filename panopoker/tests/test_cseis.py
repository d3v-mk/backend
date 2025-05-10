import json
from sqlalchemy import create_engine, Column, Integer, Float, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.dialects.postgresql import JSON

# Avaliação
from panopoker.poker.game.avaliar_maos import RANKING
from panopoker.poker.game.DistribuidorDePote import DistribuidorDePote



# Um jogador larga (fold) antes do showdown, mas já havia apostado. 
# Testa se a aposta dele vai pro pote e não volta pra ele.

Base = declarative_base()

class Mesa(Base):
    __tablename__ = "mesas"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    buy_in = Column(Float)
    status = Column(String, default="aberta")
    limite_jogadores = Column(Integer, default=6)
    jogador_da_vez = Column(Integer, nullable=True)
    estado_da_rodada = Column(String, default="pre-flop")
    dealer_pos = Column(Integer, nullable=True)
    small_blind = Column(Float)
    big_blind = Column(Float)
    posicao_sb = Column(Integer, nullable=True)
    posicao_bb = Column(Integer, nullable=True)
    pote_total = Column(Float, default=0.0)
    aposta_atual = Column(Float, default=0.0)
    cartas_comunitarias = Column(JSON, default=dict)
    vencedores_ultima_rodada = Column(JSON, default=list)

    jogadores = relationship("JogadorNaMesa", back_populates="mesa", lazy="select")
    def __repr__(self):
        return f"<Mesa {self.id} - {self.nome} ({self.status})>"

class JogadorNaMesa(Base):
    __tablename__ = "jogadores_na_mesa"
    id = Column(Integer, primary_key=True, index=True)
    mesa_id = Column(Integer, ForeignKey("mesas.id"))
    foldado = Column(Boolean, default=False)
    jogador_id = Column(Integer)
    posicao_cadeira = Column(Integer, nullable=True)
    rodada_ja_agiu = Column(Boolean, default=False)
    participando_da_rodada = Column(Boolean, default=True)
    saldo_inicial = Column(Float)
    saldo_atual = Column(Float)
    aposta_atual = Column(Float, default=0.0)
    aposta_acumulada = Column(Float, default=0.0)
    cartas = Column(JSON, nullable=True, default=list)

    mesa = relationship("Mesa", back_populates="jogadores")
    def __repr__(self):
        return f"<JogadorNaMesa {self.jogador_id} - Mesa {self.mesa_id}>"

if __name__ == "__main__":
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.create_all(engine)

    mesa = Mesa(
        id=1,
        nome="Mesa Fold Pre-Showdown",
        estado_da_rodada="river",
        cartas_comunitarias={
            "flop": ["10E", "JE", "QE"],
            "turn": "4C",
            "river": "4P"
        },
        pote_total=0.0
    )
    session.add(mesa)
    session.commit()

    jogadores = [
        JogadorNaMesa(
            jogador_id=1,
            mesa_id=1,
            saldo_inicial=1.0,
            saldo_atual=0.0,
            aposta_acumulada=1.0,
            aposta_atual=1.0,
            cartas=json.dumps(["2P", "2C"]),
            participando_da_rodada=False,
            foldado=True
        ),
        JogadorNaMesa(
            jogador_id=2,
            mesa_id=1,
            saldo_inicial=1.0,
            saldo_atual=0.0,
            aposta_acumulada=1.0,
            aposta_atual=1.0,
            cartas=json.dumps(["3P", "3C"]),
            participando_da_rodada=True,
            foldado=False
        ),
        JogadorNaMesa(
            jogador_id=3,
            mesa_id=1,
            saldo_inicial=1.0,
            saldo_atual=0.0,
            aposta_acumulada=1.0,
            aposta_atual=1.0,
            cartas=json.dumps(["4E", "4O"]),
            participando_da_rodada=True,
            foldado=False
        )
    ]
    session.add_all(jogadores)
    session.commit()

    distr = DistribuidorDePote(mesa, session)
    resultado = distr.realizar_showdown()

    print("\n================= 🟡 RESULTADO DO SHOWDOWN =================\n")
    for item in resultado["showdown"]:
        id_jog = item["jogador_id"]
        cartas = item["cartas"]
        rank_tipo, rank_vals = item["rank"]
        nome_rank = next(k for k, v in RANKING.items() if v == rank_tipo)
        print(f"Jogador {id_jog}: {' '.join(cartas)}  | Rank: {nome_rank.upper()} ({rank_vals})")

    print("\n🏆 Vencedores:")
    for vid in resultado["vencedores"]:
        print(f"→ Jogador {vid}")

    print("\n💰 Saldos finais:")
    for j in session.query(JogadorNaMesa).filter_by(mesa_id=1).order_by(JogadorNaMesa.jogador_id):
        print(f"Jogador {j.jogador_id}: saldo_final = R${j.saldo_atual:.2f}")
    print("\n============================================================\n")
