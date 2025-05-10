from fastapi import HTTPException
from sqlalchemy.orm import Session
from panopoker.poker.models.mesa import Mesa, JogadorNaMesa

def get_mesa(db: Session, mesa_id: int) -> Mesa:
    mesa = db.query(Mesa).filter_by(id=mesa_id).first()
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa não encontrada.")
    return mesa

def get_jogador(db: Session, mesa_id: int, jogador_id: int) -> JogadorNaMesa:
    jogador = db.query(JogadorNaMesa).filter_by(mesa_id=mesa_id, jogador_id=jogador_id).first()
    if not jogador:
        raise HTTPException(status_code=404, detail="Jogador não encontrado na mesa.")
    return jogador

def get_jogadores_da_mesa(db: Session, mesa_id: int):
    return db.query(JogadorNaMesa).filter_by(mesa_id=mesa_id).all()

def verificar_vez(jogador: JogadorNaMesa, mesa: Mesa):
    if jogador.jogador_id != mesa.jogador_da_vez_id:
        raise HTTPException(status_code=403, detail="Não é sua vez de jogar.")
