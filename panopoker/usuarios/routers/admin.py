from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from panopoker.core.database import get_db
from panopoker.poker.models.mesa import JogadorNaMesa
from panopoker.core.debug import debug_print
from panopoker.poker.models.mesa import Mesa
from panopoker.usuarios.models.usuario import Usuario

router = APIRouter(prefix="/admin", tags=["Admin"])

# ============================= FORCA LIMPAR A MESA TOTALMENTE (remove players tbm) =============================

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


# ============================= FORCA O SHOWDOWN PRA TESTES =============================

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

# ============================= PROMOVER USUARIO A PROMOTER =============================

@router.post("/usuario/promover/{user_id}")
def promover_usuario(user_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).get(user_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    usuario.is_promoter = True
    db.commit()
    return {"msg": "Usuário promovido a promotor"}



# ============================= CRIAR LOJA DOS PROMOTERS ==================================

from pydantic import BaseModel
from panopoker.usuarios.models.promotor import Promotor


class LojaPromotorInput(BaseModel):
    slug: str

    # Pix copia e cola
    pix_copiaecola_3: str | None = None
    pix_copiaecola_5: str | None = None
    pix_copiaecola_10: str | None = None
    pix_copiaecola_20: str | None = None
    pix_copiaecola_50: str | None = None
    pix_copiaecola_100: str | None = None

@router.post("/promotores/{user_id}/criar_loja")
def criar_loja_promotor(user_id: int, dados: LojaPromotorInput, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if not usuario.is_promoter:
        raise HTTPException(status_code=403, detail="Usuário não é um promotor")

    if db.query(Promotor).filter(Promotor.user_id == user_id).first():
        raise HTTPException(status_code=400, detail="Loja já cadastrada para este usuário")

    if db.query(Promotor).filter(Promotor.slug == dados.slug).first():
        raise HTTPException(status_code=400, detail="Slug já está em uso")

    loja = Promotor(
        user_id=user_id,
        nome=usuario.nome,
        slug=dados.slug,
        avatar_url=usuario.avatar_url,

        # Pix Copia e Cola
        pix_copiaecola_3=dados.pix_copiaecola_3,
        pix_copiaecola_5=dados.pix_copiaecola_5,
        pix_copiaecola_10=dados.pix_copiaecola_10,
        pix_copiaecola_20=dados.pix_copiaecola_20,
        pix_copiaecola_50=dados.pix_copiaecola_50,
        pix_copiaecola_100=dados.pix_copiaecola_100,
    )

    db.add(loja)
    db.commit()

    return {"status": "ok", "slug": dados.slug}

