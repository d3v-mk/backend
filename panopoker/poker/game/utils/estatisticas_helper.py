from typing import List, Tuple, Dict
from panopoker.poker.models.mesa import JogadorNaMesa
from panopoker.poker.game.AtualizadorDeEstatisticas import AtualizadorDeEstatisticas
from decimal import Decimal

def registrar_estatisticas_showdown(
    participantes: List[JogadorNaMesa],
    payload_showdown: List[dict],
    side_pots: List[Tuple[Decimal, List[JogadorNaMesa]]],  # Agora é Decimal!
    db
):
    """
    Atualiza estatísticas de showdown, ignorando side-pots zero e usando dados do payload.
    """
    jogadores_avaliados: List[Tuple[JogadorNaMesa, List[str], int]] = []
    valores_ganhos: Dict[int, Decimal] = {}
    vencedores_ids: List[int] = []

    # Mapeia id -> jogador para buscas eficientes
    jogadores_dict: Dict[int, JogadorNaMesa] = {j.jogador_id: j for j in participantes}

    # Avalia mãos de quem não foldou, usando tipo_mao do payload
    for resultado in payload_showdown:
        if resultado.get("foldado", False):
            continue
        j_id = resultado["jogador_id"]
        jogador = jogadores_dict.get(j_id)
        if not jogador:
            continue
        mao = resultado.get("cartas", [])
        tipo_mao = resultado.get("tipo_mao", 0)
        jogadores_avaliados.append((jogador, mao, tipo_mao))

    # Distribui os side pots, ignorando valores zero
    for amount, grupo in side_pots:
        # Se vier float por acidente, força pra Decimal:
        amount = Decimal(str(amount))
        if amount <= Decimal("0.00"):
            continue
        resultados = []  # List[Tuple[JogadorNaMesa, Tuple[int,List[int]]]]
        for j in grupo:
            # Extrai dados do payload para este jogador
            payload_item = next(item for item in payload_showdown if item["jogador_id"] == j.jogador_id)
            tipo_mao = payload_item.get("tipo_mao", 0)
            valores_mao = payload_item.get("valores_mao", [])
            resultados.append((j, (tipo_mao, valores_mao)))
        # Ordena por (rank, kickers)
        resultados.sort(key=lambda x: (x[1][0], x[1][1]), reverse=True)
        melhor_hand = resultados[0][1]
        winners = [j for j, hand in resultados if hand == melhor_hand]
        ganho = (amount / Decimal(len(winners))).quantize(Decimal("0.01"))
        for w in winners:
            valores_ganhos[w.jogador_id] = valores_ganhos.get(w.jogador_id, Decimal("0.00")) + ganho
            vencedores_ids.append(w.jogador_id)

    # Grava no banco
    AtualizadorDeEstatisticas.atualizar(
        jogadores_avaliados=jogadores_avaliados,
        vencedores_ids=list(set(vencedores_ids)),
        valores_ganhos=valores_ganhos,
        db=db
    )
