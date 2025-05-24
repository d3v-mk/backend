from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from panopoker.core.database import get_db
from panopoker.core.security import get_current_user
from panopoker.poker.models.mesa import Mesa, JogadorNaMesa, EstadoDaMesa
from panopoker.usuarios.models.usuario import Usuario
import json
from panopoker.core.debug import debug_print
from panopoker.poker.game.mesa_utils import get_mesa
from panopoker.poker.game.ControladorDePartida import ControladorDePartida
from panopoker.poker.game.avaliar_maos import avaliar_mao
from typing import List



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
        raise HTTPException(status_code=404, detail="Jogador não encontrado na mesa")

    if jogador.saldo_atual <= 0 or not jogador.participando_da_rodada:
        return {
            "cartas": [],
            "mao_formada": ""
        }

    try:
        cartas = json.loads(jogador.cartas) if jogador.cartas else []

        mesa = db.query(Mesa).filter_by(id=mesa_id).first()
        cartas_comunitarias: List[str] = []
        estado = mesa.estado_da_rodada

        if isinstance(mesa.cartas_comunitarias, dict):
            flop = mesa.cartas_comunitarias.get("flop", [])
            turn = mesa.cartas_comunitarias.get("turn")
            river = mesa.cartas_comunitarias.get("river")

            if estado in (EstadoDaMesa.FLOP, EstadoDaMesa.TURN, EstadoDaMesa.RIVER, EstadoDaMesa.SHOWDOWN):
                cartas_comunitarias.extend(flop)
            if estado in (EstadoDaMesa.TURN, EstadoDaMesa.RIVER, EstadoDaMesa.SHOWDOWN):
                if isinstance(turn, list):
                    cartas_comunitarias.extend(turn)
                elif isinstance(turn, str):
                    cartas_comunitarias.append(turn)
            if estado in (EstadoDaMesa.RIVER, EstadoDaMesa.SHOWDOWN):
                if isinstance(river, list):
                    cartas_comunitarias.extend(river)
                elif isinstance(river, str):
                    cartas_comunitarias.append(river)

        todas_cartas = cartas + cartas_comunitarias

        if len(todas_cartas) >= 5:
            tipo_mao, _ = avaliar_mao(todas_cartas)

            mao_legivel = {
                1: "Carta Alta",
                2: "Par",
                3: "Dois Pares",
                4: "Trinca",
                5: "Sequência",
                6: "Flush",
                7: "Full House",
                8: "Quadra",
                9: "Straight Flush",
                10: "Royal Flush"
            }.get(tipo_mao, "Indefinida")

            return {
                "cartas": cartas,
                "mao_formada": mao_legivel
            }

        return {
            "cartas": cartas,
            "mao_formada": ""
        }

    except Exception as e:
        return {
            "cartas": [],
            "mao_formada": ""
        }




    


@router.get("/{mesa_id}/cartas_comunitarias")
def get_cartas_comunitarias(
    mesa_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
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

    return {"cartas_comunitarias": cartas_visiveis} ##

