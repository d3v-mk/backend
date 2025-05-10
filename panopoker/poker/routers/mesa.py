from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from panopoker.core.database import get_db
from panopoker.poker.models.mesa import Mesa
from panopoker.poker.game.DistribuidorDePote import DistribuidorDePote
from panopoker.poker.game.avaliar_maos import RANKING
from panopoker.core.debug import debug_print
from panopoker.poker.models.mesa import JogadorNaMesa
import json
from panopoker.poker.game.avaliar_maos import avaliar_mao
from panopoker.usuarios.models.usuario import Usuario



router = APIRouter(prefix="/mesa", tags=["Showdown"])

@router.get("/{mesa_id}/showdown")
def obter_resultado_showdown(
    mesa_id: int,
    db: Session = Depends(get_db)
):
    mesa = db.query(Mesa).filter_by(id=mesa_id).first()
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa não encontrada")

    if mesa.estado_da_rodada != "showdown":
        raise HTTPException(status_code=400, detail="Showdown ainda não ocorreu")

    jogadores = (
        db.query(JogadorNaMesa)
        .filter(JogadorNaMesa.mesa_id == mesa_id)
        .all()
    )

    # Se o pote já foi distribuído, só calcula os dados a partir do que está no banco
    if mesa.pote_total == 0:
        debug_print("[GET SHOWDOWN] Evitando reprocessar showdown — pote já distribuído")

        comunitarias = (
            mesa.cartas_comunitarias
            if isinstance(mesa.cartas_comunitarias, dict)
            else json.loads(mesa.cartas_comunitarias)
        )
        cartas_mesa = []
        cartas_mesa.extend(comunitarias.get("flop", []))
        if comunitarias.get("turn"): cartas_mesa.append(comunitarias["turn"])
        if comunitarias.get("river"): cartas_mesa.append(comunitarias["river"])

        showdown_info = [
            {
                "jogador_id": j.jogador_id,
                "cartas": json.loads(j.cartas) if j.cartas else [],
                "rank": avaliar_mao(cartas_mesa + (json.loads(j.cartas) if j.cartas else [])),
                "foldado": j.foldado
            }
            for j in jogadores
        ]

        # pega os vencedores com a melhor mão que não deram fold
        melhor_rank = max((j["rank"] for j in showdown_info if not j["foldado"]), default=(0,))
        vencedores = [j["jogador_id"] for j in showdown_info if j["rank"] == melhor_rank and not j["foldado"]]

        resultado = {
            "vencedores": vencedores,
            "showdown": showdown_info
        }
    else:
        controlador = DistribuidorDePote(mesa, db)
        resultado = controlador.realizar_showdown()

    # Pega nomes com base nos IDs
    vencedores_nomes = (
        db.query(Usuario.nome)
        .filter(Usuario.id.in_(resultado["vencedores"]))
        .all()
    )
    nomes = [v[0] for v in vencedores_nomes]  # pega só os nomes da tupla

    primeiro_vencedor = resultado["vencedores"][0] if resultado["vencedores"] else None

    mao_vencedora = next(
        (j for j in resultado["showdown"] if j["jogador_id"] == primeiro_vencedor),
        None
    )
    rank_valor = mao_vencedora["rank"][0] if mao_vencedora else None
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
    }.get(rank_valor, "Indefinida")

    pote_distribuido = round(sum(j.aposta_atual for j in jogadores), 2)

    return {
        "vencedores": nomes,
        "mao_formada": mao_legivel,
        "pote": pote_distribuido
    }
