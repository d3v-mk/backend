from typing import List, Tuple, Set, Dict
import json
from collections import defaultdict

from panopoker.poker.models.mesa import JogadorNaMesa
from panopoker.poker.game.avaliar_maos import avaliar_mao, identificar_cartas_usadas_completo, descrever_mao
from panopoker.core.debug import debug_print


def wincards_helper(
    jogadores: List[JogadorNaMesa],
    cartas_mesa: List[str],
    vencedores_ids: Set[int]
) -> List[dict]:
    showdown_payload = []

    for j in jogadores:
        hole = json.loads(j.cartas) if isinstance(j.cartas, str) else j.cartas

        tipo_mao, valores_mao = avaliar_mao(hole + cartas_mesa)
        usadas = identificar_cartas_usadas_completo(hole, cartas_mesa, valores_mao, tipo_mao)

        debug_print(f"[SD DEBUG] jogador {j.jogador_id} tipo_mao={tipo_mao}, valores={valores_mao}")
        debug_print(f"[SD DEBUG] cartas utilizadas by jogador {j.jogador_id}: {usadas}")

        descricao = descrever_mao(tipo_mao, valores_mao)

        debug_print(f"[SD DEBUG] descricao={descricao}")

        payload_item = {
            "jogador_id": j.jogador_id,
            "cartas": hole,
            "tipo_mao": tipo_mao,
            "descricao_mao": descricao,   # 👈 AQUI!
            "valores_mao": valores_mao,
            "foldado": getattr(j, "foldado", False),
            "cartas_utilizadas": usadas
        }
        showdown_payload.append(payload_item)

    return showdown_payload
