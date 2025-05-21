from typing import List, Tuple, Set, Dict
import json
from collections import defaultdict

from panopoker.poker.models.mesa import JogadorNaMesa
from panopoker.poker.game.avaliar_maos import avaliar_mao, identificar_cartas_usadas
from panopoker.core.debug import debug_print


def wincards_helper(
    jogadores: List[JogadorNaMesa],
    cartas_mesa: List[str],
    vencedores_ids: Set[int]
) -> Tuple[List[dict], List[str], List[int], Dict[int, List[str]]]:
    
    showdown_payload = []
    cartas_vencedoras_comunitarias = set()
    cartas_vencedoras_por_jogador: Dict[int, List[str]] = defaultdict(list)
    

    for j in jogadores:
        hole = json.loads(j.cartas) if isinstance(j.cartas, str) else j.cartas
        combined = hole + cartas_mesa

        # Avalia a mão completa (hole + mesa)
        tipo_mao, valores_mao = avaliar_mao(combined)
        debug_print(f"[SD DEBUG] jogador {j.jogador_id} tipo_mao={tipo_mao}, valores={valores_mao}")

        # Identifica todas as cartas usadas na combinação vencedora
        usadas = identificar_cartas_usadas(combined, valores_mao, tipo_mao)
        debug_print(f"[SD DEBUG] cartas usadas by jogador {j.jogador_id}: {usadas}")

        # Se for vencedor, separe hole vs comunitárias
        if j.jogador_id in vencedores_ids:
            hole_used = [c for c in usadas if c in hole]
            comm_used = [c for c in usadas if c in cartas_mesa]
            cartas_vencedoras_por_jogador[j.jogador_id] = hole_used
            cartas_vencedoras_comunitarias.update(comm_used)
        else:
            cartas_vencedoras_por_jogador[j.jogador_id] = []

        payload_item = {
            "jogador_id": j.jogador_id,
            "cartas": hole,
            "tipo_mao": tipo_mao,
            "valores_mao": valores_mao,
            "foldado": getattr(j, "foldado", False),
            "cartas_vencedoras": cartas_vencedoras_por_jogador[j.jogador_id]
        }
        showdown_payload.append(payload_item)

    comunitarias_vencedoras = list(cartas_vencedoras_comunitarias)
    vencedores = list(vencedores_ids)

    debug_print(f"[SD DEBUG] comunitarias usadas: {comunitarias_vencedoras}")
    debug_print(f"[SD DEBUG] cartas vencedoras por jogador: {dict(cartas_vencedoras_por_jogador)}")

    return showdown_payload, comunitarias_vencedoras, vencedores, cartas_vencedoras_por_jogador

###