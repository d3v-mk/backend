import random
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from panopoker.poker.models.mesa import Mesa, JogadorNaMesa
from panopoker.poker.game.ControladorDePartida import ControladorDePartida
from panopoker.poker.game.ExecutorDeAcoes import ExecutorDeAcoes
from panopoker.poker.game.GerenciadorDeRodada import GerenciadorDeRodada
from panopoker.core.debug import debug_print

def main():
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    session = Session()

    Mesa.metadata.create_all(engine)
    JogadorNaMesa.metadata.create_all(engine)

    mesa = Mesa(
        id=1,
        nome="Mesa Simulada",
        status="aberta",
        estado_da_rodada="pre-flop",
        small_blind=0.01,
        big_blind=0.02,
        buy_in=0.30
    )
    session.add(mesa)
    session.commit()

    for i in range(6):
        jogador = JogadorNaMesa(
            jogador_id=i + 1,
            mesa_id=mesa.id,
            posicao_cadeira=i,
            saldo_inicial=10.0,
            saldo_atual=10.0,
        )
        session.add(jogador)
    session.commit()

    cp = ControladorDePartida(mesa, session)
    cp.iniciar_partida()

    for rodada in range(3):
        debug_print(f"\n🎲 INÍCIO DA RODADA {rodada + 1}")

        for _ in range(20):  # no máximo 20 ações
            mesa = session.query(Mesa).filter_by(id=1).first()
            if mesa.estado_da_rodada == "showdown":
                break

            jogador_vez = mesa.jogador_da_vez
            if not jogador_vez:
                break

            jogador = session.query(JogadorNaMesa).filter_by(
                mesa_id=1, jogador_id=jogador_vez).first()

            if not jogador or jogador.foldado or not jogador.participando_da_rodada:
                GerenciadorDeRodada(mesa, session).verificar_proxima_etapa()
                continue

            acao = random.choice(["check", "call", "fold"])
            try:
                executor = ExecutorDeAcoes(mesa, session)
                getattr(executor, f"acao_{acao}")(jogador.jogador_id)
            except Exception as e:
                debug_print(f"❌ Erro ao executar {acao}: {str(e)}")

        mesa = session.query(Mesa).filter_by(id=1).first()
        jogadores = session.query(JogadorNaMesa).filter_by(mesa_id=1).all()
        debug_print(f"\n💰 Saldos após rodada {rodada + 1}:")
        for j in jogadores:
            debug_print(f" - Jogador {j.jogador_id}: R${j.saldo_atual:.2f}")

if __name__ == "__main__":
    main()
