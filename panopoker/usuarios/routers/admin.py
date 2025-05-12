from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from panopoker.core.database import get_db
from panopoker.poker.models.mesa import JogadorNaMesa
from panopoker.core.debug import debug_print
from panopoker.poker.models.mesa import Mesa

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.delete("/limpar/{mesa_id}")
def forcar_limpeza_mesa(mesa_id: int, db: Session = Depends(get_db)):
    jogadores = db.query(JogadorNaMesa).filter(
        JogadorNaMesa.mesa_id == mesa_id,
        JogadorNaMesa.foldado == True,
        JogadorNaMesa.participando_da_rodada == False,
        JogadorNaMesa.aposta_atual == 0
    ).all()

    if not jogadores:
        debug_print(f"[FORCAR_LIMPEZA] Nenhum jogador pendente de limpeza na mesa {mesa_id}")
        return {"status": "nenhum jogador para remover"}

    for j in jogadores:
        debug_print(f"[FORCAR_LIMPEZA] Removendo jogador {j.jogador_id} da mesa {mesa_id}")
        db.delete(j)

    db.commit()
    return {"status": "ok", "removidos": [j.jogador_id for j in jogadores]}


@router.delete("/limparhard/{mesa_id}")
def forcar_limpeza_mesa(mesa_id: int, db: Session = Depends(get_db)):
    jogadores = db.query(JogadorNaMesa).filter(
        JogadorNaMesa.mesa_id == mesa_id,
    ).all()
    
    for j in jogadores:
        debug_print(f"[FORCAR_LIMPEZA] Removendo jogador {j.jogador_id} da mesa {mesa_id}")
        db.delete(j)

    mesa = db.query(Mesa).filter(Mesa.id == mesa_id).first()
    if mesa:
        mesa.status = "aberta"
        mesa.estado_da_rodada = "pre-flop"
        mesa.jogador_da_vez = None
        mesa.dealer_pos = None
        mesa.posicao_sb = None
        mesa.posicao_bb = None
        mesa.pote_total = 0
        mesa.flop = []
        mesa.turn = []
        mesa.river = []
        debug_print(f"[FORCAR_LIMPEZA] Mesa {mesa_id} resetada para status 'aberta'")

    db.commit()
    return {"status": "ok", "removidos": [j.jogador_id for j in jogadores]}



@router.post("/{mesa_id}/debug/forcar_showdown")
def debug_forcar_showdown(
    mesa_id: int,
    db: Session = Depends(get_db)
):
    mesa = db.query(Mesa).filter_by(id=mesa_id).first()
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa não encontrada")

    mesa.estado_da_rodada = "showdown"
    #mesa.pote_total = 0.88  # valor fictício só pra aparecer na UI
    db.add(mesa)
    db.commit()

    debug_print(f"[DEBUG] Forçado estado SHOWDOWN na mesa {mesa.id}")
    return {"detail": "Estado forçado para showdown"}