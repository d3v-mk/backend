from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from panopoker.poker.models.mesa import Mesa, JogadorNaMesa
from panopoker.poker.game.ControladorDePartida import ControladorDePartida
from panopoker.core.debug import debug_print
import json

def test_iniciar_partida():
    # Setup do banco em memória
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Criação das tabelas
    Mesa.metadata.create_all(engine)
    JogadorNaMesa.metadata.create_all(engine)

    # Criar mesa
    mesa = Mesa(
    id=1,
    nome="Teste Início",
    status="aberta",
    estado_da_rodada="pre-flop",
    small_blind=0.01,
    big_blind=0.02,
    buy_in=0.30  # se tiver esse campo no modelo
    )

    session.add(mesa)
    session.commit()

    # Criar dois jogadores
    jogador1 = JogadorNaMesa(jogador_id=1, mesa_id=1, posicao_cadeira=0, saldo_inicial=5.0, saldo_atual=5.0)
    jogador2 = JogadorNaMesa(jogador_id=2, mesa_id=1, posicao_cadeira=1, saldo_inicial=5.0, saldo_atual=5.0)
    session.add_all([jogador1, jogador2])
    session.commit()

    # Iniciar a partida
    cp = ControladorDePartida(mesa, session)
    cp.iniciar_partida()

    # Recoleta mesa e jogadores
    mesa = session.query(Mesa).filter_by(id=1).first()
    jogadores = session.query(JogadorNaMesa).filter_by(mesa_id=1).all()

    # Coleta todas as cartas
    todas_cartas = []

    # Cartas comunitárias
    cartas_comunitarias = mesa.cartas_comunitarias or {}
    flop = cartas_comunitarias.get("flop", [])
    turn = [cartas_comunitarias.get("turn")] if cartas_comunitarias.get("turn") else []
    river = [cartas_comunitarias.get("river")] if cartas_comunitarias.get("river") else []
    comunitarias = flop + turn + river

    todas_cartas.extend(comunitarias)
    debug_print(f"[TESTE] Cartas comunitárias: {comunitarias}")

    # Cartas dos jogadores
    for j in jogadores:
        if isinstance(j.cartas, str):
            j_cartas = json.loads(j.cartas)
        else:
            j_cartas = j.cartas
        todas_cartas.extend(j_cartas)
        debug_print(f"[TESTE] Jogador {j.jogador_id} cartas: {j_cartas}")

    # Validação de duplicatas
    if len(todas_cartas) != len(set(todas_cartas)):
        print("🚨 ERRO: Cartas duplicadas detectadas!")
        print(f"Cartas totais: {todas_cartas}")
    else:
        print("✅ Sucesso: Todas as cartas são únicas!")

if __name__ == "__main__":
    test_iniciar_partida()
