'''from sqlalchemy import func
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from panopoker.poker.models.mesa import Mesa
from panopoker.core.database import get_db
from sqlalchemy import func, or_

router = APIRouter()

@router.get("/matchmaking/bronze")
def matchmaking_bronze(db: Session = Depends(get_db)):
    # 1. Prioriza mesas bronze com 1 a 5 jogadores que estejam abertas ou em jogo
    mesa_com_jogador = db.query(Mesa)\
        .join(Mesa.jogadores)\
        .filter(Mesa.buy_in == 0.30)\
        .filter(or_(Mesa.status == "aberta", Mesa.status == "em_jogo"))\
        .group_by(Mesa.id)\
        .having(func.count(Mesa.jogadores).between(1, 5))\
        .first()

    if mesa_com_jogador:
        return mesa_com_jogador

    # 2. Se não achou, pega qualquer mesa bronze com vaga e que esteja aberta
    mesas_vazias = db.query(Mesa)\
        .filter(Mesa.buy_in == 0.30)\
        .filter(Mesa.status == "aberta")\
        .all()

    for mesa in mesas_vazias:
        if len(mesa.jogadores) < 6:
            return mesa

    raise HTTPException(status_code=404, detail="Nenhuma mesa bronze disponível com vaga.")


@router.get("/matchmaking/prata")
def matchmaking_prata(db: Session = Depends(get_db)):
    # 1. Prioriza mesas bronze com 1 a 5 jogadores que estejam abertas ou em jogo
    mesa_com_jogador = db.query(Mesa)\
        .join(Mesa.jogadores)\
        .filter(Mesa.buy_in == 2)\
        .filter(or_(Mesa.status == "aberta", Mesa.status == "em_jogo"))\
        .group_by(Mesa.id)\
        .having(func.count(Mesa.jogadores).between(1, 5))\
        .first()

    if mesa_com_jogador:
        return mesa_com_jogador

    # 2. Se não achou, pega qualquer mesa prata com vaga e que esteja aberta
    mesas_vazias = db.query(Mesa)\
        .filter(Mesa.buy_in == 2)\
        .filter(Mesa.status == "aberta")\
        .all()

    for mesa in mesas_vazias:
        if len(mesa.jogadores) < 6:
            return mesa

    raise HTTPException(status_code=404, detail="Nenhuma mesa bronze disponível com vaga.")


@router.get("/matchmaking/ouro")
def matchmaking_ouro(db: Session = Depends(get_db)):
    # 1. Prioriza mesas bronze com 1 a 5 jogadores que estejam abertas ou em jogo
    mesa_com_jogador = db.query(Mesa)\
        .join(Mesa.jogadores)\
        .filter(Mesa.buy_in == 5)\
        .filter(or_(Mesa.status == "aberta", Mesa.status == "em_jogo"))\
        .group_by(Mesa.id)\
        .having(func.count(Mesa.jogadores).between(1, 5))\
        .first()

    if mesa_com_jogador:
        return mesa_com_jogador

    # 2. Se não achou, pega qualquer mesa ouro com vaga e que esteja aberta
    mesas_vazias = db.query(Mesa)\
        .filter(Mesa.buy_in == 5)\
        .filter(Mesa.status == "aberta")\
        .all()

    for mesa in mesas_vazias:
        if len(mesa.jogadores) < 6:
            return mesa

    raise HTTPException(status_code=404, detail="Nenhuma mesa bronze disponível com vaga.")'''