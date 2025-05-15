import pytest
from panopoker.poker.game.avaliar_maos import avaliar_mao, VALORES, RANKING

# Helper to convert card values to indices
def idxs(vals):
    return sorted([VALORES.index(v) for v in vals], reverse=True)


def test_high_card():
    # No pair or better, top 5 cards: A, K, J, 7, 5
    mao = ['2P', '4O', 'JP', 'KO', 'AE', '7C', '5E']
    rank, vals = avaliar_mao(mao)
    assert rank == RANKING['high_card']
    assert vals == idxs(['A', 'K', 'J', '7', '5'])


def test_one_pair():
    # One pair of Queens, kickers A, 10, 8
    mao = ['QP', 'QO', 'AE', '10C', '8E', '3O', '2C']
    rank, vals = avaliar_mao(mao)
    assert rank == RANKING['one_pair']
    assert vals == [VALORES.index('Q')] * 2 + idxs(['A', '10', '8'])


def test_two_pair():
    # Two pairs: Jacks and 7s, kicker 5
    mao = ['JP', 'JO', '7C', '7E', '5P', '2O', '3C']
    rank, vals = avaliar_mao(mao)
    assert rank == RANKING['two_pair']
    top2 = [VALORES.index('J'), VALORES.index('7')]
    kicker = VALORES.index('5')
    assert vals == [top2[0]] * 2 + [top2[1]] * 2 + [kicker]


def test_three_of_a_kind():
    # Three 9s, kickers A, 5
    mao = ['9P', '9O', '9C', 'AE', '2O', '5P', '3C']
    rank, vals = avaliar_mao(mao)
    assert rank == RANKING['three_of_a_kind']
    kickers = idxs(['A', '5'])
    assert vals == [VALORES.index('9')] * 3 + kickers


def test_straight():
    # Straight 6-7-8-9-10
    mao = ['6P', '7O', '8C', '9E', '10P', '2O', '3C']
    rank, vals = avaliar_mao(mao)
    assert rank == RANKING['straight']
    assert vals == idxs(['10', '9', '8', '7', '6'])


def test_wheel_straight():
    # Wheel A-2-3-4-5
    mao = ['AE', '2O', '3C', '4E', '5P', '9O', 'JC']
    rank, vals = avaliar_mao(mao)
    assert rank == RANKING['straight']
    # Ace-low represented as 5-4-3-2-A
    sl = ['5', '4', '3', '2', 'A']
    expected = [VALORES.index(v) for v in sl]
    assert vals == expected


def test_flush():
    # Flush in Copas (C), top cards: A, J, 9, 6, 2
    mao = ['AC', 'JC', '9C', '6C', '2C', '3O', '4E']
    rank, vals = avaliar_mao(mao)
    assert rank == RANKING['flush']
    assert vals == idxs(['A', 'J', '9', '6', '2'])


def test_full_house():
    # Full house: three 10s and two 4s
    mao = ['10P', '10O', '10C', '4E', '4O', '2P', '3C']
    rank, vals = avaliar_mao(mao)
    assert rank == RANKING['full_house']
    assert vals == [VALORES.index('10')] * 3 + [VALORES.index('4')] * 2


def test_four_of_a_kind():
    # Four kings, kicker A
    mao = ['KP', 'KO', 'KC', 'KE', 'AE', '2O', '3C']
    rank, vals = avaliar_mao(mao)
    assert rank == RANKING['four_of_a_kind']
    assert vals == [VALORES.index('K')] * 4 + [VALORES.index('A')]


def test_straight_flush_and_royal():
    # Straight flush 9-10-J-Q-K in Copas (C)
    mao = ['9C', '10C', 'JC', 'QC', 'KC', '2O', '3E']
    rank, vals = avaliar_mao(mao)
    assert rank == RANKING['straight_flush']
    assert vals == idxs(['K', 'Q', 'J', '10', '9'])

    # Royal flush in Ouros (O)
    mao_rf = ['10O', 'JO', 'QO', 'KO', 'AO', '2P', '3C']
    rank2, vals2 = avaliar_mao(mao_rf)
    assert rank2 == RANKING['royal_flush']
    assert vals2 == idxs(['A', 'K', 'Q', 'J', '10'])


if __name__ == '__main__':
    import pytest, sys
    # Run this test file directly with pytest
    sys.exit(pytest.main(['-q', __file__]))
