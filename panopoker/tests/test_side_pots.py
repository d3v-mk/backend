import pytest

# Stub class to simulate JogadorNaMesa for side-pot calculations
test_ready = False

class StubPlayer:
    def __init__(self, jogador_id, aposta_acumulada):
        self.jogador_id = jogador_id
        self.aposta_acumulada = aposta_acumulada

# Import the DistribuidorDePote implementation
from panopoker.poker.game.DistribuidorDePote import DistribuidorDePote

# Create a dummy DistribuidorDePote without actual DB dependencies
distributor = DistribuidorDePote(mesa=None, db=None)


def test_simple_side_pot():
    """
    Cenário: três jogadores, todos apostam o mesmo valor (50).
    Esperado: um único pote principal de 50 * 3 = 150 envolvendo todos.
    """
    players = [StubPlayer(1, 50), StubPlayer(2, 50), StubPlayer(3, 50)]
    side_pots = distributor._calcular_side_pots(players)
    assert len(side_pots) == 1
    amount, group = side_pots[0]
    assert amount == 150
    assert {p.jogador_id for p in group} == {1, 2, 3}


def test_two_side_pots():
    """
    Cenário: quatro jogadores com apostas desiguais:
      - J1 aposta 100
      - J2 all-in com 60
      - J3 all-in menor com 30
      - J4 paga full 100
    Esperado:
      1. Main pot: 30*4 = 120 entre [1,2,3,4]
      2. Side pot 1: (60-30)*3 = 90 entre [1,2,4]
      3. Side pot 2: (100-60)*2 = 80 entre [1,4]
    """
    players = [
        StubPlayer(1, 100),
        StubPlayer(2, 60),
        StubPlayer(3, 30),
        StubPlayer(4, 100),
    ]
    side_pots = distributor._calcular_side_pots(players)
    # Deve criar exatamente 3 potes
    assert len(side_pots) == 3
    expected = [
        (120, {1, 2, 3, 4}),
        (90,  {1, 2, 4}),
        (80,  {1, 4}),
    ]
    for (amt, group), (exp_amt, exp_set) in zip(side_pots, expected):
        assert amt == exp_amt
        assert {p.jogador_id for p in group} == exp_set


if __name__ == '__main__':
    # Permite rodar manualmente
    pytest.main([__file__])
