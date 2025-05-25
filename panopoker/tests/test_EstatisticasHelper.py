import pytest
import json

from panopoker.poker.game.utils.estatisticas_helper import registrar_estatisticas_showdown
from panopoker.poker.game.AtualizadorDeEstatisticas import AtualizadorDeEstatisticas

# stub que só grava quando for invocado
class StubAtualizador:
    called = False
    args = None

    @classmethod
    def atualizar(cls, *, jogadores_avaliados, vencedores_ids, valores_ganhos, db):
        cls.called = True
        cls.args = {
            "jogadores_avaliados": jogadores_avaliados,
            "vencedores_ids": vencedores_ids,
            "valores_ganhos": valores_ganhos,
            "db": db
        }

@pytest.fixture(autouse=True)
def patch_atualizador(monkeypatch):
    # substitui apenas o método atualizar
    monkeypatch.setattr(AtualizadorDeEstatisticas, "atualizar", StubAtualizador.atualizar)
    yield
    # limpa entre testes
    StubAtualizador.called = False
    StubAtualizador.args = None

class DummyJogador:
    def __init__(self, jogador_id, cartas, foldado=False):
        self.jogador_id = jogador_id
        self.cartas = json.dumps(cartas)
        self.foldado = foldado

class DummyDB:
    pass

def test_registrar_estatisticas_simples():
    p1 = DummyJogador(1, ["AH","KH"])
    p2 = DummyJogador(2, ["2D","3C"])
    payload = [
        {"jogador_id": 1, "cartas": ["AH","KH"], "tipo_mao": 6, "valores_mao": [12,11,10,9,8], "foldado": False},
        {"jogador_id": 2, "cartas": ["2D","3C"], "tipo_mao": 4, "valores_mao": [2,2,2,12,11], "foldado": False},
    ]
    side_pots = [
        (0.04, [p1, p2]),
        (0.00, [p1])  # deve ignorar
    ]

    registrar_estatisticas_showdown(
        participantes=[p1,p2],
        payload_showdown=payload,
        side_pots=side_pots,
        db=DummyDB()
    )

    assert StubAtualizador.called
    args = StubAtualizador.args
    # só p1 ganhou
    assert args["vencedores_ids"] == [1]
    assert args["valores_ganhos"] == {1: pytest.approx(0.04)}
    # quem não foldou entrou na lista
    assert [j.jogador_id for j,_,_ in args["jogadores_avaliados"]] == [1,2]

def test_registrar_estatisticas_empate_board_only():
    p1 = DummyJogador(1, ["4H","7S"])
    p2 = DummyJogador(2, ["5D","8C"])
    p3 = DummyJogador(3, ["6D","9C"])
    payload = [
        {"jogador_id": 1, "cartas": ["4H","7S"], "tipo_mao": 5, "valores_mao": [6,5,4,3,2], "foldado": False},
        {"jogador_id": 2, "cartas": ["5D","8C"], "tipo_mao": 5, "valores_mao": [6,5,4,3,2], "foldado": False},
        {"jogador_id": 3, "cartas": ["6D","9C"], "tipo_mao": 5, "valores_mao": [6,5,4,3,2], "foldado": False},
    ]
    side_pots = [(0.09, [p1,p2,p3])]

    registrar_estatisticas_showdown(
        participantes=[p1,p2,p3],
        payload_showdown=payload,
        side_pots=side_pots,
        db=DummyDB()
    )

    args = StubAtualizador.args
    # os três empatam
    assert set(args["vencedores_ids"]) == {1,2,3}
    # cada um leva 0.03
    assert args["valores_ganhos"] == {
        1: pytest.approx(0.03),
        2: pytest.approx(0.03),
        3: pytest.approx(0.03),
    }

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
