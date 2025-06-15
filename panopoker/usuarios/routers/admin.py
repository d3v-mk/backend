from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from panopoker.core.database import get_db
from panopoker.poker.models.mesa import Mesa
from panopoker.usuarios.models.usuario import Usuario
from panopoker.usuarios.models.promotor import Promotor
from panopoker.core.security import get_current_user_optional
from fastapi.templating import Jinja2Templates
from panopoker.lobby.models.noticias import Noticia
from panopoker.schemas.usuario import NoticiaAdminCreate
from decimal import Decimal

router = APIRouter(prefix="/api", tags=["Admin"])

templates = Jinja2Templates(directory="panopoker/site/templates")




# 🔍 Apenas CONSULTAR
@router.get("/visitas")
def consultar_visitas(db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter_by(id=1).first()
    if not usuario:
        return {"total": 0}
    return {"total": usuario.visitas_ao_site}

# ➕ Registrar uma nova visita
@router.post("/registrar/visita")
def contar_visita(request: Request, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter_by(id=1).first()
    if not usuario:
        usuario = Usuario(id=1, visitas_ao_site=1)
        db.add(usuario)
        db.commit()
        return {"mensagem": "Primeira visita registrada!"}

    usuario.visitas_ao_site += 1
    db.commit()
    return {"mensagem": "Visita registrada com sucesso!", "total": usuario.visitas_ao_site}




@router.post("/admin/ativar-manutencao")
def ativar_manutencao(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user_optional)
):
    if usuario is None:
        raise HTTPException(status_code=401, detail="Você precisa estar logado.")

    if not getattr(usuario, "is_admin", False):
        raise HTTPException(status_code=403, detail="Sem permissão, jovem gafanhoto.")

    mesas = db.query(Mesa).all()
    for mesa in mesas:
        if mesa.status == "em_jogo":
            mesa.manutencao_pendente = True
            print(f"🕒 Mesa {mesa.id} EM JOGO → manutenção agendada na próxima rodada.")
        elif mesa.status == "aberta":
            mesa.status = "manutencao"
            mesa.manutencao_pendente = False
            # aqui você pode opcionalmente avisar/kikar jogadores se já tiver alguém
            print(f"🔌 Mesa {mesa.id} ABERTA → manutenção imediata.")
    db.commit()
    return {"msg": "Manutenção ativada. Mesas em jogo serão encerradas na próxima rodada, mesas abertas já foram encerradas."}


@router.post("/admin/encerrar-manutencao")
def encerrar_manutencao(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user_optional)
):
    if usuario is None:
        raise HTTPException(status_code=401, detail="Você precisa estar logado.")

    if not getattr(usuario, "is_admin", False):
        raise HTTPException(status_code=403, detail="Sem permissão, jovem gafanhoto.")

    mesas = db.query(Mesa).filter(Mesa.status == "manutencao").all()
    restauradas = []

    for mesa in mesas:
        mesa.status = "aberta"
        mesa.manutencao_pendente = False
        restauradas.append(mesa.id)
        print(f"✅ Mesa {mesa.id} restaurada: status=aberta")

    db.commit()

    return {
        "msg": "Mesas fora da manutenção foram reabertas com sucesso.",
        "mesas_reabertas": restauradas
    }



from sqlalchemy import text

@router.delete("/noticias/limpar")
def limpar_noticias(db: Session = Depends(get_db), user: Usuario = Depends(get_current_user_optional)):
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Sem permissão, jovem gafanhoto.")

    qtd = db.query(Noticia).delete()
    db.commit()

    # Detectar qual banco tá usando
    engine_name = db.bind.dialect.name

    if engine_name == 'sqlite':
        db.execute(text("DELETE FROM sqlite_sequence WHERE name='noticias';"))
    elif engine_name == 'postgresql':
        db.execute(text("ALTER SEQUENCE noticias_id_seq RESTART WITH 1;"))
    else:
        # outros bancos, se quiser tratar
        pass

    db.commit()

    return {"ok": True, "msg": "notícias deletadas e IDs resetados"}



@router.post("/criar/noticias/admin", status_code=201)
def criar_noticia_admin(
    payload: NoticiaAdminCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user_optional)  # agora usando optional
):
    if usuario is None:
        raise HTTPException(status_code=401, detail="Você precisa estar logado.")

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
    return noticia


# ============================= PROMOVER USUARIO A PROMOTER =============================

@router.post("/admin/usuario/promover/{user_id}")
def promover_usuario(
    user_id: int,
    tipo: str,  # "admin" ou "promotor"
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user_optional)
):
    if usuario is None:
        raise HTTPException(status_code=401, detail="Você precisa estar logado.")

    if not getattr(usuario, "is_admin", False):
        raise HTTPException(status_code=403, detail="Sem permissão, jovem padawan.")

    usuario_alvo = db.query(Usuario).get(user_id)
    if not usuario_alvo:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if tipo == "admin":
        usuario_alvo.is_admin = True
    elif tipo == "promotor":
        usuario_alvo.is_promoter = True
    else:
        raise HTTPException(status_code=400, detail="Tipo inválido. Use 'admin' ou 'promotor'.")

    db.commit()
    return {"msg": f"Usuário promovido a {tipo} (sem perder cargos anteriores)"}






@router.post("/admin/usuario/despromover/{user_id}")
def despromover_usuario(
    user_id: int,
    tipo: str,  # "admin" ou "promotor"
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user_optional)
):
    if usuario is None:
        raise HTTPException(status_code=401, detail="Você precisa estar logado.")

    if not getattr(usuario, "is_admin", False):
        raise HTTPException(status_code=403, detail="Sem permissão, jovem padawan.")

    usuario_alvo = db.query(Usuario).get(user_id)
    if not usuario_alvo:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if tipo == "admin":
        usuario_alvo.is_admin = False
    elif tipo == "promotor":
        usuario_alvo.is_promoter = False
    else:
        raise HTTPException(status_code=400, detail="Tipo inválido. Use 'admin' ou 'promotor'.")

    db.commit()
    return {"msg": f"Usuário removido do cargo de {tipo}"}



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



from fastapi.responses import JSONResponse
from decimal import Decimal

@router.post("/admin/promotor/{promotor_id}/desbloquear")
async def desbloquear_promotor(
    promotor_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_current_user_optional)
):
    try:
        if not admin or not admin.is_admin:
            return JSONResponse(status_code=403, content={"erro": "Apenas administradores podem acessar."})

        promotor = db.query(Promotor).filter(Promotor.id == promotor_id).first()
        if not promotor:
            return JSONResponse(status_code=404, content={"erro": "Promotor não encontrado"})

        promotor.bloqueado = False
        promotor.saldo_repassar = Decimal("0.00")
        promotor.comissao_total = Decimal("0.00")

        db.add(promotor)
        db.commit()

        return JSONResponse(status_code=200, content={
            "status": "ok",
            "mensagem": f"Promotor {promotor_id} desbloqueado com sucesso"
        })
    
    except Exception as e:
        print("Erro ao desbloquear:", e)
        return JSONResponse(status_code=500, content={"erro": str(e)})











# ============================================================
from pydantic import BaseModel

class PromotorCreate(BaseModel):
    user_id: int
    user_id_mp: str
    access_token: str
    refresh_token: str
    nome: str | None = None


@router.post("/admin/promotor/criar_loja")
def criar_loja_promotor(promotor_data: PromotorCreate, db: Session = Depends(get_db)):
    data = promotor_data
    user_id = data.user_id
    user_id_mp = data.user_id_mp
    access_token = data.access_token
    refresh_token = data.refresh_token
    nome = data.nome

    promotor = db.query(Promotor).filter(Promotor.user_id == user_id).first()

    if not promotor:
        promotor = Promotor(
            user_id=user_id,
            user_id_mp=user_id_mp,
            access_token=access_token,
            refresh_token=refresh_token,
            slug=f"promotor_{user_id}",
            nome=nome or "Loja do Promotor"
        )
        db.add(promotor)
    else:
        promotor.user_id_mp = user_id_mp
        promotor.access_token = access_token
        promotor.refresh_token = refresh_token
        if nome:
            promotor.nome = nome
        if not promotor.slug:
            promotor.slug = f"promotor_{user_id}"

    db.commit()

    return {"msg": "Promotor criado ou atualizado com sucesso!", "promotor_id": promotor.id}




# ============================= FORCA LIMPAR A MESA TOTALMENTE (remove players tbm) =============================

from panopoker.poker.models.mesa import JogadorNaMesa
from panopoker.core.debug import debug_print

@router.delete("/admin/limparhard/{mesa_id}")
def forcar_limpeza_mesa(
    mesa_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user_optional)
):
    if usuario is None:
        raise HTTPException(status_code=401, detail="Você precisa estar logado.")

    if not getattr(usuario, "is_admin", False):
        raise HTTPException(status_code=403, detail="Sem permissão para usar o sabre de luz da destruição total.")

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

# ============================================================












# ==== so pra ver oq o showdown ta retornando ====
# @router.post("/admin/{mesa_id}/debug/executar_showdown")
# async def executar_showdown_debug(mesa_id: int, db: Session = Depends(get_db)):
#     mesa = db.query(Mesa).filter(Mesa.id == mesa_id).first()
#     if not mesa:
#         raise HTTPException(status_code=404, detail="Mesa não encontrada")

#     controlador = DistribuidorDePote(mesa=mesa, db=db)
#     resultado = await controlador.realizar_showdown()
#     return resultado







# @router.post("/admin/promotor/criar_loja")
# def criar_loja_promotor(
#     user_id: int,
#     nome: str,
#     slug: str,
#     access_token: str = "",
#     refresh_token: str = "",
#     db: Session = Depends(get_db),
#     admin: Usuario = Depends(get_current_user_optional)
# ):
#     if not admin.is_admin:
#         raise HTTPException(status_code=403, detail="Apenas administradores podem acessar.")

#     usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
#     if not usuario:
#         raise HTTPException(status_code=404, detail="Usuário não encontrado.")

#     promotor_existente = db.query(Promotor).filter(Promotor.user_id == user_id).first()
#     if promotor_existente:
#         raise HTTPException(status_code=400, detail="Este usuário já possui uma loja.")

#     nova_loja = Promotor(
#         user_id=user_id,
#         user_id_mp="manual",
#         nome=nome,
#         slug=slug,
#         access_token=access_token,
#         refresh_token=refresh_token
#     )

#     db.add(nova_loja)
#     db.commit()

#     return {"status": "ok", "mensagem": "Loja criada com sucesso."}



# ============================= FORCA O SHOWDOWN PRA TESTES =============================

# @router.post("/admin/{mesa_id}/debug/forcar_showdown")
# def debug_forcar_showdown(
#     mesa_id: int,
#     db: Session = Depends(get_db),
#     usuario: Usuario = Depends(get_current_user_optional)
# ):
#     if usuario is None:
#         raise HTTPException(status_code=401, detail="Você precisa estar logado.")

#     if not getattr(usuario, "is_admin", False):
#         raise HTTPException(status_code=403, detail="Acesso negado, agente secreto sem credencial.")

#     mesa = db.query(Mesa).filter_by(id=mesa_id).first()
#     if not mesa:
#         raise HTTPException(status_code=404, detail="Mesa não encontrada")

#     mesa.estado_da_rodada = "showdown"
#     db.add(mesa)
#     db.commit()

#     debug_print(f"[DEBUG] Forçado estado SHOWDOWN na mesa {mesa.id}")
#     return {"detail": "Estado forçado para showdown"}









# @router.delete("/admin/reset_estatisticas")
# def resetar_estatisticas(
#     db: Session = Depends(get_db),
#     usuario: Usuario = Depends(get_current_user_optional)
# ):
#     if usuario is None:
#         raise HTTPException(status_code=401, detail="Você precisa estar logado.")

#     if not getattr(usuario, "is_admin", False):
#         raise HTTPException(status_code=403, detail="Sem permissão, jovem gafanhoto.")

#     estatisticas = db.query(EstatisticasJogador).all()
#     if not estatisticas:
#         raise HTTPException(status_code=404, detail="Nenhuma estatística encontrada")

#     for stat in estatisticas:
#         stat.rodadas_jogadas = 0
#         stat.rodadas_ganhas = 0
#         stat.vitorias = 0
#         stat.fichas_ganhas = 0.0
#         stat.fichas_perdidas = 0.0
#         stat.maior_pote = 0.0
#         stat.data_primeira_vitoria = None
#         stat.data_ultima_vitoria = None
#         stat.mao_favorita = None
#         stat.sequencias = 0
#         stat.flushes = 0
#         stat.fullhouses = 0
#         stat.quadras = 0
#         stat.straight_flushes = 0
#         stat.royal_flushes = 0
#         stat.ultimo_update = None
#         db.add(stat)

#     db.commit()
#     return {"mensagem": "Estatísticas resetadas com sucesso"}
