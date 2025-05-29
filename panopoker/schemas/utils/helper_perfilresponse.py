from fastapi import Request
from typing import Optional
from datetime import datetime
from panopoker.schemas.usuario import PerfilResponse

def build_perfil_response(
    usuario,
    estatisticas,
    request: Optional[Request] = None
):
    # Base URL do avatar
    avatar_url = usuario.avatar_url or ""
    if request:
        base_url = str(request.base_url).rstrip("/")
        if avatar_url.startswith("/"):
            avatar_url = f"{base_url}{avatar_url}"
        elif avatar_url.startswith("http://api.panopoker.com") or avatar_url.startswith("https://api.panopoker.com"):
            avatar_url = avatar_url.replace("http://api.panopoker.com", base_url)
            avatar_url = avatar_url.replace("https://api.panopoker.com", base_url)


    # Campos de estatísticas, ou zero/null se não tiver
    stats = estatisticas
    return PerfilResponse(
        id_publico=usuario.id_publico,
        nome=usuario.nome,
        avatar_url=avatar_url,
        is_promoter=getattr(usuario, "is_promoter", False),

        rodadas_ganhas=stats.rodadas_ganhas if stats else 0,
        rodadas_jogadas=stats.rodadas_jogadas if stats else 0,
        fichas_ganhas=stats.fichas_ganhas if stats else 0.0,
        fichas_perdidas=stats.fichas_perdidas if stats else 0.0,
        sequencias=stats.sequencias if stats else 0,
        flushes=stats.flushes if stats else 0,
        full_houses=stats.full_houses if stats else 0,
        quadras=stats.quadras if stats else 0,
        straight_flushes=stats.straight_flushes if stats else 0,
        royal_flushes=stats.royal_flushes if stats else 0,
        torneios_vencidos=stats.torneios_vencidos if stats else 0,
        maior_pote=stats.maior_pote if stats else 0.0,
        vitorias=stats.vitorias if stats else 0,
        mao_favorita=stats.mao_favorita if stats and stats.mao_favorita else None,
        ranking_mensal=stats.ranking_mensal if stats else None,
        vezes_no_top1=stats.vezes_no_top1 if stats else 0,
        data_primeira_vitoria=stats.data_primeira_vitoria if stats and stats.data_primeira_vitoria else None,
        data_ultima_vitoria=stats.data_ultima_vitoria if stats and stats.data_ultima_vitoria else None,
        ultimo_update=stats.ultimo_update if stats and stats.ultimo_update else None,
        beta_tester=stats.beta_tester if stats else 0
    )
