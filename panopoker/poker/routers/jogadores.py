from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from panopoker.core.database import get_db
from panopoker.poker.game.mesa_utils import get_mesa
from panopoker.poker.game.ControladorDePartida import ControladorDePartida
from panopoker.poker.models.mesa import JogadorNaMesa
from panopoker.core.debug import debug_print
from panopoker.core.security import get_current_user
from panopoker.usuarios.models.usuario import Usuario
from panopoker.websocket.manager import connection_manager
import asyncio
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
            "is_dealer": j.posicao_cadeira == mesa.dealer_pos,
        })
        debug_print(
            f"[LISTAR_JOGADORES] Incluído jogador {j.jogador_id} "
            f"(foldado={j.foldado}, saldo={j.saldo_atual:.2f})", silent=True
        )

    debug_print(f"[LISTAR_JOGADORES] Resposta final montada para mesa {mesa_id}", silent=True)
    return resposta


@router.post("/{mesa_id}/revelar_cartas")
def revelar_cartas(
    mesa_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    mesa = get_mesa(db, mesa_id)

    jogador = db.query(JogadorNaMesa).filter_by(mesa_id=mesa.id, jogador_id=usuario.id).first()
    if not jogador:
        raise HTTPException(status_code=404, detail="Jogador não encontrado na mesa")

    jogador.participando_da_rodada = True
    db.commit()

    # Notifica via websocket (forma compatível com FastAPI sync route)
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.create_task(connection_manager.broadcast_mesa(
        mesa_id,
        {
            "evento": "revelar_cartas",
            "jogador_id": usuario.id
        }
    ))

    return {"message": "Cartas agora são públicas para todos."}