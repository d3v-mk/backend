from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from panopoker.core.database import get_db
from panopoker.core.security import get_current_user
from panopoker.models.mesa import JogadorNaMesa
from panopoker.usuarios.models.usuario import Usuario
import json
from panopoker.core.debug import debug_print
from panopoker.poker.game.mesa_utils import get_mesa
from panopoker.poker.game.ControladorDePartida import ControladorDePartida
from panopoker.models.mesa import Mesa

router = APIRouter(prefix="/mesa", tags=["Baralho"])


# Cartas do jogador
@router.get("/{mesa_id}/minhas_cartas")
def minhas_cartas(
    mesa_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    debug_print(f"[MINHAS_CARTAS] Jogador {current_user.id} solicitou suas cartas na mesa {mesa_id}", silent=True)

    jogador = (
        db.query(JogadorNaMesa)
          .filter_by(mesa_id=mesa_id, jogador_id=current_user.id)
          .first()
    )

    if not jogador:
        debug_print(f"[MINHAS_CARTAS][ERRO] Jogador {current_user.id} não encontrado na mesa {mesa_id}")
        raise HTTPException(status_code=404, detail="Jogador não encontrado na mesa")

    # se zerou o saldo ou não está participando da rodada, retorna lista vazia
    if jogador.saldo_atual <= 0 or not jogador.participando_da_rodada:
        debug_print(
            f"[MINHAS_CARTAS] Jogador {current_user.id} sem saldo ou fora da rodada — retornando []",
            silent=True
        )
        return []

    try:
        cartas = json.loads(jogador.cartas) if jogador.cartas else []
        debug_print(f"[MINHAS_CARTAS] Cartas retornadas para jogador {current_user.id}: {cartas}", silent=True)
        return cartas
    except Exception as e:
        debug_print(
            f"[MINHAS_CARTAS][ERRO] Erro ao carregar cartas do jogador {current_user.id} "
            f"na mesa {mesa_id}: {str(e)}"
        )
        return []

    


@router.get("/{mesa_id}/cartas_comunitarias")
def get_cartas_comunitarias(
    mesa_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    debug_print(f"[CARTAS_COMUNITARIAS] Jogador {current_user.id} solicitou cartas da mesa {mesa_id}", silent=True)

    mesa = db.query(Mesa).filter(Mesa.id == mesa_id).first()
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa não encontrada.")

    # 🧠 Garante que é um dict válido, mesmo se estiver como string no banco
    try:
        if isinstance(mesa.cartas_comunitarias, str):
            cartas = json.loads(mesa.cartas_comunitarias)
        else:
            cartas = mesa.cartas_comunitarias or {}
    except:
        cartas = {}

    # 🧠 Garante que as chaves sempre existam
    flop = cartas.get("flop", [])
    turn = cartas.get("turn")
    river = cartas.get("river")

    estado = mesa.estado_da_rodada or "pre-flop"
    cartas_visiveis = {"flop": [], "turn": None, "river": None}

    if estado in ["flop", "turn", "river", "showdown"]:
        cartas_visiveis["flop"] = flop
    if estado in ["turn", "river", "showdown"]:
        cartas_visiveis["turn"] = turn
    if estado in ["river", "showdown"]:
        cartas_visiveis["river"] = river

    debug_print(f"[CARTAS_COMUNITARIAS] Mesa {mesa.id} | Estado: {estado} | Retornando: {cartas_visiveis}", silent=True)

    return {"cartas_comunitarias": cartas_visiveis}





@router.get("/{mesa_id}")
def get_mesa_completa(
    mesa_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    mesa = db.query(Mesa).filter(Mesa.id == mesa_id).first()
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa não encontrada.")

    return {
        "id": mesa.id,
        "nome": mesa.nome,
        "buy_in": mesa.buy_in,
        "status": mesa.status,
        "limite_jogadores": mesa.limite_jogadores,
        "jogador_da_vez": mesa.jogador_da_vez,
        "estado_da_rodada": mesa.estado_da_rodada,
        "dealer_pos": mesa.dealer_pos,
        "small_blind": mesa.small_blind,
        "big_blind": mesa.big_blind,
        "pote_total": mesa.pote_total,
        "aposta_atual": mesa.aposta_atual,
        "cartas_comunitarias": mesa.cartas_comunitarias,
    }