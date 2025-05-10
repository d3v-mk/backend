from collections import Counter
from typing import List, Tuple

VALORES = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

RANKING = {
    "high_card": 1,
    "one_pair": 2,
    "two_pair": 3,
    "three_of_a_kind": 4,
    "straight": 5,
    "flush": 6,
    "full_house": 7,
    "four_of_a_kind": 8,
    "straight_flush": 9,
    "royal_flush": 10
}

def extrair_valor(carta: str) -> str:
    return "10" if carta.startswith("10") else carta[:-1]

def encontrar_straight(valores: List[int]) -> List[int] | None:
    s = sorted(set(valores))
    for i in range(len(s) - 4):
        if s[i+4] - s[i] == 4:
            return sorted(s[i:i+5], reverse=True)
    if set([12, 0, 1, 2, 3]).issubset(s):
        return [3, 2, 1, 0, 12]
    return None

def avaliar_mao(mao: List[str]) -> Tuple[int, List[int]]:
    valores_idx = [VALORES.index(extrair_valor(c)) for c in mao]
    naipes = [c[-1] for c in mao]
    vc = Counter(valores_idx)
    nc = Counter(naipes)

    flush_naipe = next((n for n, count in nc.items() if count >= 5), None)

    if flush_naipe:
        cartas_flush = [c for c in mao if c[-1] == flush_naipe]
        valores_flush = [VALORES.index(extrair_valor(c)) for c in cartas_flush]
        sf = encontrar_straight(valores_flush)

        if sf:
            # Verifica se todas as cartas do straight estão no mesmo naipe
            cartas_esperadas = [VALORES[v] + flush_naipe for v in sf]
            if all(c in cartas_flush for c in cartas_esperadas):
                if sf == [12, 11, 10, 9, 8]:
                    return RANKING["royal_flush"], sf
                return RANKING["straight_flush"], sf

    quad = [v for v, c in vc.items() if c == 4]
    if quad:
        v = quad[0]
        kicker = max([x for x in valores_idx if x != v], default=0)
        return RANKING["four_of_a_kind"], [v]*4 + [kicker]

    trips = sorted([v for v, c in vc.items() if c == 3], reverse=True)
    pairs = sorted([v for v, c in vc.items() if c == 2], reverse=True)
    if trips:
        if len(trips) > 1:
            return RANKING["full_house"], [trips[0]]*3 + [trips[1]]*2
        if pairs:
            return RANKING["full_house"], [trips[0]]*3 + [pairs[0]]*2

    if flush_naipe:
        topf = sorted([VALORES.index(extrair_valor(c)) for c in mao if c[-1] == flush_naipe], reverse=True)[:5]
        return RANKING["flush"], topf

    straight_vals = encontrar_straight(valores_idx)
    if straight_vals:
        return RANKING["straight"], straight_vals

    if trips:
        v = trips[0]
        kickers = sorted([x for x in valores_idx if x != v], reverse=True)[:2]
        return RANKING["three_of_a_kind"], [v]*3 + kickers

    if len(pairs) >= 2:
        top2 = pairs[:2]
        kicker = max([x for x in valores_idx if x not in top2], default=0)
        return RANKING["two_pair"], [top2[0]]*2 + [top2[1]]*2 + [kicker]

    if len(pairs) == 1:
        p = pairs[0]
        kickers = sorted([x for x in valores_idx if x != p], reverse=True)[:3]
        return RANKING["one_pair"], [p]*2 + kickers

    top5 = sorted(valores_idx, reverse=True)[:5]
    return RANKING["high_card"], top5
