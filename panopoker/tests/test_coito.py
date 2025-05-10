# Arquivo: test_showdown.py

import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# --- Patch para desabilitar o agendamento de nova rodada e o próprio nova_rodada ---
from panopoker.poker.game.ResetadorDePartida import ResetadorDePartida
ResetadorDePartida.nova_rodada = lambda self: None

# Se houver algum schedule interno no DistribuidorDePote, a gente remove também:
from panopoker.poker.game.DistribuidorDePote import DistribuidorDePote
DistribuidorDePote._agendar_nova_rodada = lambda self: None  # se existir

# --- Imports principais ---
from panopoker.poker.models.mesa import Mesa, JogadorNaMesa
from panopoker.poker.game.avaliar_maos import RANKING
from panopoker.poker.game.DistribuidorDePote import DistribuidorDePote

def run_scenario(nome, community, hole_cards, stack_hero=5.0):
    # setup em memória
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    session = Session()
    Mesa.metadata.create_all(engine)
    JogadorNaMesa.metadata.create_all(engine)

    # cria mesa
    mesa = Mesa(
        id=1,
        nome=nome,
        estado_da_rodada="river",
        cartas_comunitarias=community,
        pote_total=0.0,
        aposta_atual=stack_hero
    )
    session.add(mesa)
    session.commit()

    # herói do cenário
    hero = JogadorNaMesa(
        jogador_id=1,
        mesa_id=mesa.id,
        saldo_inicial=stack_hero,
        saldo_atual=0.0,
        aposta_acumulada=stack_hero,
        aposta_atual=stack_hero,
        cartas=hole_cards,
        participando_da_rodada=True,
        foldado=False
    )
    # oponente dummy (sempre perde, aposta só 1)
    dummy = JogadorNaMesa(
        jogador_id=2,
        mesa_id=mesa.id,
        saldo_inicial=1.0,
        saldo_atual=0.0,
        aposta_acumulada=1.0,
        aposta_atual=1.0,
        cartas=["2E","3C"],
        participando_da_rodada=True,
        foldado=False
    )
    session.add_all([hero, dummy])
    session.commit()

    distr = DistribuidorDePote(mesa, session)
    resultado = distr.realizar_showdown()

    # imprime resumo
    print(f"\n=== Cenário: {nome} ===")
    for item in resultado["showdown"]:
        rank_tipo, rank_vals = item["rank"]
        nome_rank = next(k for k, v in RANKING.items() if v == rank_tipo)
        marc = "🏆" if item["jogador_id"] in resultado["vencedores"] else "   "
        print(f"{marc} J{item['jogador_id']}: {nome_rank} {rank_vals}")
    print(f"Vencedor(es): {resultado['vencedores']}")
    print("- saldos finais:")
    for j in session.query(JogadorNaMesa).order_by(JogadorNaMesa.jogador_id):
        print(f"   J{j.jogador_id}: R${j.saldo_atual:.2f}")

def main():
    cenarios = {
        "High Card": {
            "community": {"flop": ["2E","5C","9O"], "turn": "JO", "river": "KC"},
            "hole": ["3P","7E"]
        },
        "One Pair": {
            "community": {"flop": ["5E","7C","2O"], "turn": "JO", "river": "KC"},
            "hole": ["KC","3P"]
        },
        "Two Pair": {
            "community": {"flop": ["6E","6C","9O"], "turn": "9P", "river": "2O"},
            "hole": ["3E","4C"]
        },
        "Three of a Kind": {
            "community": {"flop": ["8E","8C","8O"], "turn": "4P", "river": "JO"},
            "hole": ["3E","5C"]
        },
        "Straight": {
            "community": {"flop": ["4E","5C","6O"], "turn": "7P", "river": "9O"},
            "hole": ["8E","2C"]
        },
        "Flush": {
            "community": {"flop": ["2O","5O","9O"], "turn": "KO", "river": "3C"},
            "hole": ["JO","4O"]
        },
        "Full House": {
            "community": {"flop": ["3E","3C","3O"], "turn": "9P", "river": "9C"},
            "hole": ["3P","2C"]
        },
        "Four of a Kind": {
            "community": {"flop": ["4E","4C","4O"], "turn": "8P", "river": "KO"},
            "hole": ["4P","9O"]
        },
        "Straight Flush": {
            "community": {"flop": ["6O","7O","8O"], "turn": "9O", "river": "JO"},
            "hole": ["10O","2C"]
        },
        "Royal Flush": {
            "community": {"flop": ["10O","JO","QO"], "turn": "KO", "river": "AO"},
            "hole": ["2E","3C"]
        }
    }

    for nome, data in cenarios.items():
        run_scenario(nome, data["community"], data["hole"])

if __name__ == "__main__":
    main()
