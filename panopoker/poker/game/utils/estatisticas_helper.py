from datetime import datetime
from typing import List, Tuple, Dict
from panopoker.usuarios.models.estatisticas import EstatisticasJogador
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
    jogadores_avaliados = []
    valores_ganhos = {}
    vencedores_ids = []

    jogadores_dict = {j.jogador_id: j for j in participantes}

    for resultado in payload_showdown:
        jogador_id = resultado["jogador_id"]
        if resultado["foldado"]:
            continue
        jogador = jogadores_dict[jogador_id]
        mao = resultado["cartas"]
        rank = resultado["rank"][0]
        jogadores_avaliados.append((jogador, mao, rank))

    for amount, grupo in side_pots:
        resultados = []
        for j in grupo:
            hole = j.cartas if isinstance(j.cartas, list) else json.loads(j.cartas)
            resultados.append((j, avaliar_mao(hole)))  # cartas comunitárias já estão incluídas antes
        winners = sorted(resultados, key=lambda x: (x[1][0], x[1][1]), reverse=True)
        melhor = winners[0][1]
        vencedores = [j for j, r in winners if r == melhor]
        ganho = amount / len(vencedores) if vencedores else 0
        for w in vencedores:
            valores_ganhos[w.jogador_id] = valores_ganhos.get(w.jogador_id, 0) + ganho
            vencedores_ids.append(w.jogador_id)

    AtualizadorDeEstatisticas.atualizar(
        jogadores_avaliados=jogadores_avaliados,
        vencedores_ids=list(set(vencedores_ids)),
        valores_ganhos=valores_ganhos,
        db=db
    )
