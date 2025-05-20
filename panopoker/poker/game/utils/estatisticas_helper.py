from datetime import datetime
from typing import List, Tuple, Dict
from panopoker.poker.models.mesa import JogadorNaMesa
from panopoker.poker.game.AtualizadorDeEstatisticas import AtualizadorDeEstatisticas
from panopoker.poker.game.avaliar_maos import avaliar_mao
import json

def registrar_estatisticas_showdown(
    participantes: List[JogadorNaMesa],
    payload_showdown: List[dict],
    side_pots: List[Tuple[float, List[JogadorNaMesa]]],
    db
):
    jogadores_avaliados: List[Tuple[JogadorNaMesa, List[str], int]] = []
    valores_ganhos: Dict[int, float] = {}
    vencedores_ids: List[int] = []

    # Mapeia id -> jogador para buscas eficientes
    jogadores_dict: Dict[int, JogadorNaMesa] = {j.jogador_id: j for j in participantes}

    # Avalia mãos de quem não foldou
    for resultado in payload_showdown:
        jogador_id = resultado.get("jogador_id")
        if resultado.get("foldado", False):
            continue

        jogador = jogadores_dict.get(jogador_id)
        if not jogador:
            # Jogador não encontrado nos participantes, ignora
            continue

        mao = resultado.get("cartas", [])
        rank = resultado.get("rank", [0])[0]
        jogadores_avaliados.append((jogador, mao, rank))

    # Distribui os side pots
    for amount, grupo in side_pots:
        resultados = []
        for j in grupo:
            # Garante lista de strings para as cartas
            hole_cards = j.cartas if isinstance(j.cartas, list) else json.loads(j.cartas)
            resultados.append((j, avaliar_mao(hole_cards)))
        # Ordena por rank e kickers
        winners_sorted = sorted(
            resultados,
            key=lambda x: (x[1][0], x[1][1]),
            reverse=True
        )
        melhor_rank = winners_sorted[0][1]
        vencedores = [j for j, r in winners_sorted if r == melhor_rank]
        if vencedores:
            ganho = amount / len(vencedores)
            for w in vencedores:
                valores_ganhos[w.jogador_id] = valores_ganhos.get(w.jogador_id, 0) + ganho
                vencedores_ids.append(w.jogador_id)

    # Atualiza estatísticas no banco
    AtualizadorDeEstatisticas.atualizar(
        jogadores_avaliados=jogadores_avaliados,
        vencedores_ids=list(set(vencedores_ids)),
        valores_ganhos=valores_ganhos,
        db=db
    )
