from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from panopoker.core.database import get_db
from panopoker.poker.game.mesa_utils import get_mesa
from panopoker.poker.game.ControladorDePartida import ControladorDePartida
from panopoker.poker.models.mesa import JogadorNaMesa
from panopoker.core.debug import debug_print
import json

router = APIRouter(prefix="/mesa", tags=["Jogadores na mesa"])

@router.get("/{mesa_id}/jogadores")
def listar_jogadores_na_mesa(
    mesa_id: int,
    db: Session = Depends(get_db)
):
    debug_print(f"[LISTAR_JOGADORES] Solicitada lista de jogadores da mesa {mesa_id}", silent=True)

    mesa = get_mesa(db, mesa_id)
    
    # 🛠️ Puxa TODOS os jogadores, sem filtro
    jogadores = db.query(JogadorNaMesa)\
        .filter(JogadorNaMesa.mesa_id == mesa.id)\
        .order_by(JogadorNaMesa.posicao_cadeira)\
        .all()

    user_id_da_vez = mesa.jogador_da_vez

    resposta = []
    for j in jogadores:
        try:
            cartas = json.loads(j.cartas) if j.cartas else []
        except Exception:
            debug_print(f"[LISTAR_JOGADORES][ERRO] Falha ao decodificar cartas do jogador {j.jogador_id}")
            cartas = []

        resposta.append({
            "id": j.id,
            "user_id": j.jogador_id,
            "username": j.jogador.nome if j.jogador else "",
            "email": j.jogador.email if j.jogador else "",
            "is_admin": j.jogador.is_admin if j.jogador else False,
            "avatarUrl": j.jogador.avatar_url if j.jogador else None,
            "saldo_inicial": j.saldo_inicial,
            "saldo_atual": j.saldo_atual,
            "aposta_atual": j.aposta_atual,
            "foldado": j.foldado,
            "rodada_ja_agiu": j.rodada_ja_agiu,
            "cartas": cartas,
            "vez": j.jogador_id == user_id_da_vez,
            "posicao_cadeira": j.posicao_cadeira,
            "participando_da_rodada": j.participando_da_rodada,
            "is_sb": j.posicao_cadeira == mesa.posicao_sb,
            "is_bb": j.posicao_cadeira == mesa.posicao_bb,
        })
        debug_print(
            f"[LISTAR_JOGADORES] Incluído jogador {j.jogador_id} "
            f"(foldado={j.foldado}, saldo={j.saldo_atual:.2f})", silent=True
        )

    debug_print(f"[LISTAR_JOGADORES] Resposta final montada para mesa {mesa_id}", silent=True)
    return resposta