from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from panopoker.core.database import get_db
from panopoker.poker.models.mesa import Mesa
from panopoker.usuarios.models.usuario import Usuario
from panopoker.poker.models.mesa import JogadorNaMesa
from panopoker.core.security import get_current_user
from panopoker.core.debug import debug_print
from panopoker.poker.game.ExecutorDeAcoes import ExecutorDeAcoes
from panopoker.poker.game.ControladorDeMesa import ControladorDeMesa



router = APIRouter(prefix="/mesa", tags=["Acoes"])

@router.post("/{mesa_id}/call")
def call(mesa_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    mesa = db.query(Mesa).filter_by(id=mesa_id).first()
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa não encontrada.")
    
    acoes = ExecutorDeAcoes(mesa, db)
    acoes.acao_call(current_user.id)


    return {"msg": f"Jogador {current_user.id} deu CALL"}


@router.post("/{mesa_id}/allin")
def allin(mesa_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    mesa = db.query(Mesa).filter_by(id=mesa_id).first()
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa não encontrada.")
    
    controlador = ExecutorDeAcoes(mesa, db)
    controlador.acao_allin(current_user.id)

    return {"msg": f"Jogador {current_user.id} foi ALL-IN"}


@router.post("/{mesa_id}/check")
def check(mesa_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    mesa = db.query(Mesa).filter_by(id=mesa_id).first()
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa não encontrada.")
    
    controlador = ExecutorDeAcoes(mesa, db)
    controlador.acao_check(current_user.id)

    return {"msg": f"Jogador {current_user.id} deu CHECK"}


@router.post("/{mesa_id}/fold")
def fold(mesa_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    mesa = db.query(Mesa).filter_by(id=mesa_id).first()
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa não encontrada.")
    
    controlador = ExecutorDeAcoes(mesa, db)
    controlador.acao_fold(current_user.id)

    return {"msg": f"Jogador {current_user.id} deu FOLD"}


@router.post("/{mesa_id}/raise")
def raise_aposta(mesa_id: int, valor: float, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    mesa = db.query(Mesa).filter_by(id=mesa_id).first()
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa não encontrada.")
    
    controlador = ExecutorDeAcoes(mesa, db)
    controlador.acao_raise(current_user.id, valor)

    return {"msg": f"Jogador {current_user.id} deu RAISE de R${valor:.2f}"}


# Endpoint para sair da mesa
@router.post("/{mesa_id}/sair")
def sair_da_mesa(
    mesa_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    mesa = db.query(Mesa).filter_by(id=mesa_id).first()

    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa não encontrada.")

    controlador = ControladorDeMesa(mesa, db)
    controlador.sair_da_mesa(current_user)

    return {"message": f"Jogador {current_user.id} saiu da mesa {mesa.nome}"}


# Endpoint para entrar na mesa
@router.post("/{mesa_id}/entrar")
def entrar_na_mesa(
    mesa_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    mesa = db.query(Mesa).filter_by(id=mesa_id).first()

    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa não encontrada.")

    controlador = ControladorDeMesa(mesa, db)
    controlador.entrar_na_mesa(current_user)

    return {"message": f"Jogador {current_user.id} entrou na mesa {mesa.nome}"}