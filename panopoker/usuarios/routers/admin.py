from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from panopoker.core.database import get_db
from panopoker.poker.models.mesa import JogadorNaMesa
from panopoker.core.debug import debug_print
from panopoker.poker.models.mesa import Mesa
from panopoker.usuarios.models.usuario import Usuario
from panopoker.usuarios.models.promotor import Promotor
from panopoker.core.security import get_current_user
from panopoker.core.security import get_current_user_optional
from panopoker.usuarios.models.estatisticas import EstatisticasJogador
from fastapi.templating import Jinja2Templates
from panopoker.poker.game.DistribuidorDePote import DistribuidorDePote
from panopoker.lobby.models.noticias import Noticia
from panopoker.schemas.usuario import NoticiaAdminCreate

router = APIRouter(tags=["Admin"])

templates = Jinja2Templates(directory="panopoker/site/templates")


@router.delete("/admin/reset_estatisticas")
def resetar_estatisticas(db: Session = Depends(get_db)):
    estatisticas = db.query(EstatisticasJogador).all()
    if not estatisticas:
        raise HTTPException(status_code=404, detail="Nenhuma estatística encontrada")

    for stat in estatisticas:
        stat.rodadas_jogadas = 0
        stat.rodadas_ganhas = 0
        stat.vitorias = 0
        stat.fichas_ganhas = 0.0
        stat.fichas_perdidas = 0.0
        stat.maior_pote = 0.0
        stat.data_primeira_vitoria = None
        stat.data_ultima_vitoria = None
        stat.mao_favorita = None
        stat.sequencias = 0
        stat.flushes = 0
        stat.fullhouses = 0
        stat.quadras = 0
        stat.straight_flushes = 0
        stat.royal_flushes = 0
        stat.ultimo_update = None
        db.add(stat)

    db.commit()
    return {"mensagem": "Estatísticas resetadas com sucesso"}


from sqlalchemy import text

@router.delete("/noticias/limpar")
def limpar_noticias(
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user)
):
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão, jovem gafanhoto."
        )

    qtd = db.query(Noticia).delete()
    db.commit()

    db.execute(text("DELETE FROM sqlite_sequence WHERE name='noticias';")) #arrumar isso qnd migrar pro PostgreSQL
    db.commit()

    return {"ok": True, "msg": f"notícias deletadas e IDs resetados"}



@router.post("/noticias/admin", status_code=201)
def criar_noticia_admin(
    payload: NoticiaAdminCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    if not getattr(usuario, "is_admin", False):
        raise HTTPException(status_code=403, detail="Sem permissão, jovem padawan.")

    noticia = Noticia(
        mensagem=payload.mensagem,
        tipo="admin",
        usuario_id=usuario.id
    )
    db.add(noticia)
    db.commit()
    db.refresh(noticia)
    return noticia  # Retorna o SQLAlchemy model (de preferência, faça um DTO/Schema, mas pra admin pode ser assim)



# ============================= FORCA LIMPAR A MESA TOTALMENTE (remove players tbm) =============================

@router.delete("/admin/limparhard/{mesa_id}")
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

@router.post("/admin/{mesa_id}/debug/forcar_showdown")
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

@router.post("/admin/usuario/promover/{user_id}")
def promover_usuario(
    user_id: int,
    tipo: str,  # "admin" ou "promotor"
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).get(user_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if tipo == "admin":
        usuario.is_admin = True  # Ativa admin, mantém promotor se já era
    elif tipo == "promotor":
        usuario.is_promoter = True  # Ativa promotor, mantém admin se já era
    else:
        raise HTTPException(status_code=400, detail="Tipo inválido. Use 'admin' ou 'promotor'.")

    db.commit()
    return {"msg": f"Usuário promovido a {tipo} (sem perder cargos anteriores)"}





@router.post("/admin/usuario/despromover/{user_id}")
def despromover_usuario(
    user_id: int,
    tipo: str,  # "admin" ou "promotor"
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).get(user_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if tipo == "admin":
        usuario.is_admin = False  # Tira só o cargo de admin
    elif tipo == "promotor":
        usuario.is_promoter = False  # Tira só o cargo de promotor
    else:
        raise HTTPException(status_code=400, detail="Tipo inválido. Use 'admin' ou 'promotor'.")

    db.commit()
    return {"msg": f"Usuário removido do cargo de {tipo}"}



@router.post("/admin/promotor/criar_loja")
def criar_loja_promotor(
    user_id: int,
    nome: str,
    slug: str,
    access_token: str = "",
    refresh_token: str = "",
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_current_user_optional)
):
    if not admin.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem acessar.")

    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    promotor_existente = db.query(Promotor).filter(Promotor.user_id == user_id).first()
    if promotor_existente:
        raise HTTPException(status_code=400, detail="Este usuário já possui uma loja.")

    nova_loja = Promotor(
        user_id=user_id,
        user_id_mp="manual",
        nome=nome,
        slug=slug,
        access_token=access_token,
        refresh_token=refresh_token
    )

    db.add(nova_loja)
    db.commit()

    return {"status": "ok", "mensagem": "Loja criada com sucesso."}



@router.post("/admin/promotor/{promotor_id}/apagar_loja")
def apagar_loja_promotor(
    promotor_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_current_user_optional)
):
    if not admin.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem acessar.")

    promotor = db.query(Promotor).filter(Promotor.id == promotor_id).first()

    if not promotor:
        raise HTTPException(status_code=404, detail="Loja do promotor não encontrada.")

    db.delete(promotor)
    db.commit()

    return {"status": "ok", "mensagem": "Loja do promotor removida com sucesso."}


# ==== so pra ver oq o showdown ta retornando ====
@router.post("/admin/{mesa_id}/debug/executar_showdown")
async def executar_showdown_debug(mesa_id: int, db: Session = Depends(get_db)):
    mesa = db.query(Mesa).filter(Mesa.id == mesa_id).first()
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa não encontrada")

    controlador = DistribuidorDePote(mesa=mesa, db=db)
    resultado = await controlador.realizar_showdown()
    return resultado
