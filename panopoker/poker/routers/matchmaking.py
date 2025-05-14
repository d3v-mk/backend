from sqlalchemy import func
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from panopoker.poker.models.mesa import Mesa
from panopoker.core.database import get_db

router = APIRouter()

@router.get("/matchmaking/bronze")
def matchmaking_bronze(db: Session = Depends(get_db)):
    # 1. Tenta priorizar mesas com jogadores
    mesa_com_jogador = db.query(Mesa)\
        .join(Mesa.jogadores)\
        .filter(Mesa.buy_in == 0.30)\
        .filter(Mesa.status == "aberta")\
        .group_by(Mesa.id)\
        .having(func.count(Mesa.jogadores) >= 1)\
        .having(func.count(Mesa.jogadores) < 6)\
        .first()

    if mesa_com_jogador:
        return mesa_com_jogador

    # 2. Se não achou nenhuma com jogador, tenta qualquer mesa bronze com vaga
    mesa_vazia = db.query(Mesa)\
        .filter(Mesa.buy_in == 0.30)\
        .filter(Mesa.status == "aberta")\
        .all()

    for mesa in mesa_vazia:
        if len(mesa.jogadores) < 6:
            return mesa

    raise HTTPException(status_code=404, detail="Nenhuma mesa bronze disponível com vaga.")


@router.get("/matchmaking/prata")
def matchmaking_prata(db: Session = Depends(get_db)):
    # 1. Tenta priorizar mesas com jogadores
    mesa_com_jogador = db.query(Mesa)\
        .join(Mesa.jogadores)\
        .filter(Mesa.buy_in == 2)\
        .filter(Mesa.status == "aberta")\
        .group_by(Mesa.id)\
        .having(func.count(Mesa.jogadores) >= 1)\
        .having(func.count(Mesa.jogadores) < 6)\
        .first()

    if mesa_com_jogador:
        return mesa_com_jogador

    # 2. Se não achou nenhuma com jogador, tenta qualquer mesa bronze com vaga
    mesa_vazia = db.query(Mesa)\
        .filter(Mesa.buy_in == 2)\
        .filter(Mesa.status == "aberta")\
        .all()

    for mesa in mesa_vazia:
        if len(mesa.jogadores) < 6:
            return mesa

    raise HTTPException(status_code=404, detail="Nenhuma mesa bronze disponível com vaga.")


@router.get("/matchmaking/ouro")
def matchmaking_ouro(db: Session = Depends(get_db)):
    # 1. Tenta priorizar mesas com jogadores
    mesa_com_jogador = db.query(Mesa)\
        .join(Mesa.jogadores)\
        .filter(Mesa.buy_in == 5)\
        .filter(Mesa.status == "aberta")\
        .group_by(Mesa.id)\
        .having(func.count(Mesa.jogadores) >= 1)\
        .having(func.count(Mesa.jogadores) < 6)\
        .first()

    if mesa_com_jogador:
        return mesa_com_jogador

    # 2. Se não achou nenhuma com jogador, tenta qualquer mesa bronze com vaga
    mesa_vazia = db.query(Mesa)\
        .filter(Mesa.buy_in == 5)\
        .filter(Mesa.status == "aberta")\
        .all()

    for mesa in mesa_vazia:
        if len(mesa.jogadores) < 6:
            return mesa

    raise HTTPException(status_code=404, detail="Nenhuma mesa bronze disponível com vaga.")