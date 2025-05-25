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
    n = len(s)
    # 1) busca de trás pra frente, pra achar a straight mais alta primeiro
    for i in range(n - 5, -1, -1):
        # ex.: i = n-5 => s[i:i+5] é último window de 5 valores
        if s[i+4] - s[i] == 4:
            # devolve em ordem descendente [alto,...,baixo]
            return sorted(s[i:i+5], reverse=True)
    # 2) roda wheel (A-2-3-4-5) só se não achou nada acima
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



from collections import Counter

# Quantidade de cartas usadas para cada tipo de mão
cartas_por_rank = {
    1: 5,   # high card
    2: 2,   # one pair
    3: 4,   # two pair (2+2)
    4: 3,   # three of a kind
    5: 5,   # straight
    6: 5,   # flush
    7: 5,   # full house (3+2)
    8: 4,   # four of a kind
    9: 5,   # straight flush
    10: 5   # royal flush
}

def extrair_valor(carta: str) -> str:
    return "10" if carta.startswith("10") else carta[:-1]


def identificar_cartas_usadas_completo(
    mao: List[str],
    mesa: List[str],
    cartas_vencedoras_valores: List[int],
    rank: int
) -> List[dict]:
    """
    Retorna as cartas usadas na melhor mão, indicando origem, índice e tipo.
    Agora filtra por naipe em casos de flush.
    """
    # Número de cartas que compõem a mão principal
    needed = cartas_por_rank.get(rank, 5)
    principais = cartas_vencedoras_valores[:needed]
    kickers = cartas_vencedoras_valores[needed:]

    # Contagem de valores
    valores_main = Counter(principais)
    valores_kicker = Counter(kickers)

    # Define o tipo principal conforme ranking
    if rank == RANKING["royal_flush"]:
        tipo_main = "royal_flush"
    elif rank == RANKING["straight_flush"]:
        tipo_main = "straight_flush"
    elif rank == RANKING["four_of_a_kind"]:
        tipo_main = "quadra"
    elif rank == RANKING["full_house"]:
        tipo_main = "full_house"
    elif rank == RANKING["flush"]:
        tipo_main = "flush"
    elif rank == RANKING["straight"]:
        tipo_main = "sequencia"
    elif rank == RANKING["three_of_a_kind"]:
        tipo_main = "trinca"
    elif rank == RANKING["two_pair"]:
        tipo_main = "dois_pares"
    elif rank == RANKING["one_pair"]:
        tipo_main = "par"
    else:
        tipo_main = "high_card"

    resultado = []

    def valor_da_carta(c: str) -> str:
        return extrair_valor(c)

    # Detecta naipe de flush caso necessário
    flush_suit = None
    if tipo_main in ("flush", "straight_flush", "royal_flush"):
        suit_counts = Counter(c[-1] for c in mao + mesa)
        flush_suit = next((s for s, cnt in suit_counts.items() if cnt >= 5), None)

    # Busca cartas principais e kickers (mão primeiro, depois mesa)
    for tipo, count_map in ((tipo_main, valores_main), ("kicker", valores_kicker)):
        for valor, count in count_map.items():
            for _ in range(count):
                # procura na mão, depois na mesa
                for origem, cartas in (('mao', mao), ('mesa', mesa)):
                    for idx, carta in enumerate(cartas):
                        # filtra por naipe de flush quando aplicável (exceto kickers)
                        if flush_suit and tipo != 'kicker' and carta[-1] != flush_suit:
                            continue
                        if VALORES.index(valor_da_carta(carta)) == valor and not any(
                            r['carta'] == carta and r['origem'] == origem and r['indice'] == idx
                            for r in resultado
                        ):
                            resultado.append({
                                'carta': carta,
                                'origem': origem,
                                'indice': idx,
                                'tipo': tipo
                            })
                            break
                    else:
                        continue
                    break
    return resultado






VALORES_NOMES = {
    2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7",
    8: "8", 9: "9", 10: "10", 11: "J", 12: "Q", 13: "K", 14: "A"
}

TIPOS_MAO = {
    1: "Carta alta",
    2: "Par",
    3: "Dois pares",
    4: "Trinca",
    5: "Sequência",
    6: "Flush",
    7: "Full house",
    8: "Quadra",
    9: "Straight flush",
    10: "Royal flush"
}

def nome_valor_poker(idx):
    try:
        return VALORES[idx]
    except Exception:
        return f"?{idx}?"

def descrever_mao(tipo_mao, valores_mao):
    def nome(idx):
        try: return VALORES[idx]
        except: return f"?{idx}?"

    if tipo_mao == 1:
        # High card: sempre mostra as 5 cartas
        return "Carta alta " + ", ".join(nome(v) for v in valores_mao)
    elif tipo_mao == 2:
        # Par: mostra todos os kickers
        return f"Par de {nome(valores_mao[0])}, kickers: {', '.join(nome(v) for v in valores_mao[2:])}"
    elif tipo_mao == 3:
        # Dois pares: kicker é o último valor
        return f"Dois pares: {nome(valores_mao[0])} e {nome(valores_mao[2])}, kicker {nome(valores_mao[4])}"
    elif tipo_mao == 4:
        # Trinca: dois kickers
        return f"Trinca de {nome(valores_mao[0])}, kickers: {', '.join(nome(v) for v in valores_mao[3:])}"
    elif tipo_mao == 5:
        return f"Sequência até {nome(valores_mao[0])}"
    elif tipo_mao == 6:
        return f"Flush até {nome(valores_mao[0])}"
    elif tipo_mao == 7:
        return f"Full house: {nome(valores_mao[0])} com {nome(valores_mao[3])}"
    elif tipo_mao == 8:
        return f"Quadra de {nome(valores_mao[0])}, kicker {nome(valores_mao[4])}"
    elif tipo_mao == 9:
        return f"Straight flush até {nome(valores_mao[0])}"
    elif tipo_mao == 10:
        return "Royal flush"
    else:
        return "Mão desconhecida"
