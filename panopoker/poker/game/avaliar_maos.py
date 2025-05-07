from collections import Counter
from itertools import combinations
from typing import List, Dict, Tuple

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

def is_sequencia(valores):
    vals = sorted(set(valores))
    for i in range(len(vals) - 4):
        if vals[i+4] - vals[i] == 4:
            return True
    if set([12, 0, 1, 2, 3]).issubset(set(vals)):
        return True
    return False

def ordenar_mao(mao):
    return sorted(mao, key=lambda c: VALORES.index(c[:-1]), reverse=True)

def avaliar_mao(mao):
    valores = [VALORES.index(c[:-1]) for c in mao if c[:-1] in VALORES]
    naipes = [c[-1] for c in mao]
    valor_count = Counter(valores)
    naipe_count = Counter(naipes)

    flush = None
    for n, count in naipe_count.items():
        if count >= 5:
            flush = [c for c in mao if c[-1] == n]
            break

    straight = is_sequencia(valores)

    if flush:
        flush_vals = [VALORES.index(c[:-1]) for c in flush]
        if is_sequencia(flush_vals):
            if max(flush_vals) == 12:
                return (RANKING["royal_flush"], ordenar_mao(flush)[:5])
            else:
                return (RANKING["straight_flush"], ordenar_mao(flush)[:5])

    for v, c in valor_count.items():
        if c == 4:
            kicker = max([k for k in valores if k != v])
            return (RANKING["four_of_a_kind"], [VALORES[v]]*4 + [VALORES[kicker]])

    trincas = [v for v, c in valor_count.items() if c == 3]
    pares = [v for v, c in valor_count.items() if c == 2]
    if trincas:
        if len(trincas) > 1:
            return (RANKING["full_house"], [VALORES[max(trincas)]]*3 + [VALORES[min(trincas)]]*2)
        elif pares:
            return (RANKING["full_house"], [VALORES[trincas[0]]]*3 + [VALORES[max(pares)]]*2)

    if flush:
        return (RANKING["flush"], [c for c in ordenar_mao(flush)[:5]])

    if straight:
        unique_vals = sorted(set(valores), reverse=True)
        return (RANKING["straight"], [VALORES[v] for v in unique_vals[:5]])

    if trincas:
        kickers = sorted([v for v in valores if v != trincas[0]], reverse=True)[:2]
        return (RANKING["three_of_a_kind"], [VALORES[trincas[0]]]*3 + [VALORES[k] for k in kickers])

    if len(pares) >= 2:
        top_pars = sorted(pares, reverse=True)[:2]
        kicker = max([v for v in valores if v not in top_pars])
        return (RANKING["two_pair"], [VALORES[top_pars[0]]]*2 + [VALORES[top_pars[1]]]*2 + [VALORES[kicker]])

    if len(pares) == 1:
        kicker = sorted([v for v in valores if v != pares[0]], reverse=True)[:3]
        return (RANKING["one_pair"], [VALORES[pares[0]]]*2 + [VALORES[k] for k in kicker])

    return (RANKING["high_card"], [VALORES[v] for v in sorted(valores, reverse=True)[:5]])