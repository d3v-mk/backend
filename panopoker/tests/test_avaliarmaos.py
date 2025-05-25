import pytest
from panopoker.poker.game.avaliar_maos import (
    avaliar_mao,
    identificar_cartas_usadas_completo,
    extrair_valor,
    encontrar_straight,
    nome_valor_poker,
    descrever_mao,
    cartas_por_rank
)

# Testes de classificação de mãos (paramétricos)
test_parameters = [
    # High Card
    pytest.param(['2P','5O','9C','KO','7E'], ['AP','3C'], 1, id='High Card A-high'),
    # One Pair
    pytest.param(['2P','5O','9C','KO','7E'], ['9P','3C'], 2, id='One Pair 9s'),
    # Three of a Kind (Trinca)
    pytest.param(['2P','5O','9C','KO','7E'], ['KP','KC'], 4, id='Trinca de Reis'),
    # Two Pair
    pytest.param(['2P','5O','5C','KO','7E'], ['2O','3C'], 3, id='Two Pair board+hand'),
    # Full House
    pytest.param(['2P','2O','5C','5P','5E'], ['9O','3C'], 7, id='Full House 5 sobre 2'),
    # Trips on board
    pytest.param(['2P','5O','5C','7P','9E'], ['5P','8O'], 4, id='Trips on board'),
    # Trips in hand
    pytest.param(['2P','5O','6C','7P','9E'], ['7O','7C'], 4, id='Trips in hand'),
    # Straight normal
    pytest.param(['7P','4P','6E','3P','5E'], ['6C','2O'], 5, id='Straight 3-7'),
    # Wheel straight
    pytest.param(['AP','2O','3C','4E','9P'], ['5O','7P'], 5, id='Wheel straight'),
    # Flush Q-high (Espadas)
    pytest.param(['8E','5E','10E','QE','2E'], ['6O','QE'], 6, id='Flush Q-high'),
    # Flush A-high (Copas)
    pytest.param(['2C','4C','6C','8C','9C'], ['AC','3C'], 6, id='Flush A-high'),
    # Full House 7 sobre K
    pytest.param(['KC','KO','KE','7P','9E'], ['7O','7C'], 7, id='Full House 7 sobre K'),
    # Four of a Kind 2s
    pytest.param(['2P','2O','2C','5P','7E'], ['2E','3C'], 8, id='Four 2s'),
    # Four of a Kind Aces
    pytest.param(['AP','AO','AC','KP','QO'], ['AE','2C'], 8, id='Four Aces'),
    # Straight Flush 5-9 (Copas)
    pytest.param(['5C','6C','7C','8C','2P'], ['9C','3O'], 9, id='Straight Flush 5-9'),
    # Royal Flush Wheel (Paus)
    pytest.param(['10P','JP','QP','KP','2O'], ['AP','3C'], 10, id='Royal Flush Wheel'),
    # Royal Flush Copas
    pytest.param(['10C','JC','QC','KC','2P'], ['AC','3O'], 10, id='Royal Flush'),
    # Board-only Straight tie
    pytest.param(['3C','4O','5C','6E','7P'], ['8O','9C'], 5, id='Board-only Straight tie'),
    # Board-only Flush tie
    pytest.param(['2C','4C','6C','8C','10C'], ['2O','3C'], 6, id='Board-only Flush tie'),
    # Board-only Two Pair tie
    pytest.param(['2P','2O','3C','3E','5P'], ['7O','9C'], 3, id='Board-only Two Pair tie'),
    # Board-only Full House tie
    pytest.param(['2P','2O','2C','3P','3O'], ['4C','5E'], 7, id='Board-only Full House tie'),
    # Board-only Four of a Kind tie
    pytest.param(['2P','2O','2C','2E','3P'], ['4C','5E'], 8, id='Board-only Four of a Kind tie'),
    # Board-only Straight Flush tie
    pytest.param(['2P','3P','4P','5P','6P'], ['7C','8E'], 9, id='Board-only Straight Flush tie'),
    # Board-only Royal Flush tie
    pytest.param(['10P','JP','QP','KP','AP'], ['2C','3E'], 10, id='Board-only Royal Flush tie'),
]

@pytest.mark.parametrize("mesa,mao,expected_rank", test_parameters)
def test_ranking_e_cartas(mesa, mao, expected_rank):
    rank, valores = avaliar_mao(mao + mesa)
    assert rank == expected_rank, f"{mesa}+{mao} → {rank}"
    usadas = identificar_cartas_usadas_completo(mao, mesa, valores, rank)
    needed = cartas_por_rank.get(rank, 5)
    total = needed + max(0, len(valores) - needed)
    assert len(usadas) == total, f"{mesa}+{mao} used {len(usadas)} vs {total}"

# Testes unitários de utilitários básicos

def test_extrair_valor():
    assert extrair_valor('10C') == '10'
    assert extrair_valor('AC') == 'A'
    assert extrair_valor('5E') == '5'

@pytest.mark.parametrize('vals, expected', [
    ([0,1,2,3,4], [4,3,2,1,0]),
    ([2,3,4,5,6], [6,5,4,3,2]),
    ([12,0,1,2,3], [3,2,1,0,12]),
    ([0,2,3,4,5,6,10], [6,5,4,3,2]),
])
def test_encontrar_straight(vals, expected):
    assert encontrar_straight(vals) == expected

def test_nome_valor_poker():
    assert nome_valor_poker(0) == '2'
    assert nome_valor_poker(9) == 'J'
    assert nome_valor_poker(99) == '?99?'

@pytest.mark.parametrize('tipo, valores, esperado', [
    (1, [12,8,7,6,0], 'Carta alta A, 10, 9, 8, 2'),
    (2, [9,9,12,8,7], 'Par de J, kickers: A, 10, 9'),
    (3, [11,11,8,8,2], 'Dois pares: K e 10, kicker 4'),
    (4, [6,6,6,12,10], 'Trinca de 8, kickers: A, Q'),
    (5, [5,4,3,2,1], 'Sequência até 7'),
    (6, [12,8,6,3,0], 'Flush até A'),
    (7, [5,5,5,2,2], 'Full house: 7 com 4'),
    (8, [1,1,1,1,4], 'Quadra de 3, kicker 6'),
    (9, [10,9,8,7,6], 'Straight flush até Q'),
    (10, [], 'Royal flush'),
])
def test_descrever_mao(tipo, valores, esperado):
    assert descrever_mao(tipo, valores) == esperado

if __name__ == '__main__':
    import pytest
    pytest.main([__file__])
