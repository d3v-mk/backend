from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Request
from sqlalchemy.orm import Session
from panopoker.usuarios.models.usuario import Usuario
from panopoker.usuarios.models.estatisticas import EstatisticasJogador
from panopoker.schemas.usuario import UserCreate, User, UserLogin
from panopoker.core.database import get_db
from panopoker.core.security import hash_password, verify_password, create_access_token, get_current_user
from datetime import timedelta
from panopoker.core.debug import debug_print
from panopoker.schemas.usuario import PerfilResponse
from PIL import Image
from io import BytesIO
import os

AVATAR_DIR = "panopoker/usuarios/media/avatars"
os.makedirs(AVATAR_DIR, exist_ok=True)

router = APIRouter(prefix="/usuario", tags=["Usuario"])

# ==================== ROTA PARA EXIBIR SALDO NO FRONT ====================
@router.get("/saldo")
def get_user_balance(
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user)
):
    return {"saldo": user.saldo}

# ==================== ROTA /me PARA EXIBIR DADOS NO FRONT ====================
@router.get("/me")
def get_usuario_logado(user: Usuario = Depends(get_current_user)):
    return {
        "id": user.id,
        "nome": user.nome,
        "id_publico": user.id_publico,
        "email": user.email
    }


# ==================== ROTA DE UPLOAD DE AVATAR ====================
@router.post("/upload_avatar")
def upload_avatar(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user)
):
    # Verifica tipo do arquivo
    if file.content_type not in ["image/jpeg", "image/png", "image/webp", "image/heic", "image/heif"]:
        raise HTTPException(status_code=400, detail="Formato inválido. Use JPEG ou PNG.")

    # Lê o conteúdo
    contents = file.file.read()

    # Verifica tamanho máximo (2MB)
    max_size_mb = 2
    if len(contents) > max_size_mb * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Imagem muito grande. Máx: 2MB.")

    # Processa e salva a imagem
    try:
        image = Image.open(BytesIO(contents))
        image = image.convert("RGB")  # garante JPEG
        image = image.resize((256, 256))

        filename = f"user_{user.id}.jpg"
        filepath = os.path.join(AVATAR_DIR, filename)
        image.save(filepath, format="JPEG")

        # Monta URL com base na requisição (compatível com ngrok ou domínio real)
        base_url = str(request.base_url).rstrip("/")
        avatar_url = f"{base_url}/media/avatars/{filename}"

        # Atualiza avatar_url no banco
        user.avatar_url = avatar_url
        db.add(user)  # ADICIONA O OBJETO MODIFICADO
        db.commit()
        db.refresh(user)  # GARANTE QUE O DADO FOI ATUALIZADO

        return {"msg": "Avatar atualizado com sucesso", "avatar_url": user.avatar_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar imagem: {str(e)}")

    

# ==================== ROTA PERFIL PARA EXIBIR PERFIL NO FRONT ====================
@router.get("/perfil", response_model=PerfilResponse)
def get_perfil_completo(
    request: Request,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user)
):
    stats = db.query(EstatisticasJogador).filter_by(usuario_id=user.id).first()

    # Garante que avatar_url tem base correta (ngrok, prod, etc)
    base_url = str(request.base_url).rstrip("/")
    avatar_url = user.avatar_url or ""
    if avatar_url.startswith("/"):
        avatar_url = f"{base_url}{avatar_url}"
    elif avatar_url.startswith("http://192.168.") or avatar_url.startswith("http://localhost"):
        avatar_url = avatar_url.replace("http://192.168.0.9:8000", base_url)

    return {
        "id_publico": user.id_publico,
        "nome": user.nome,
        "avatar_url": avatar_url,

        # Estatísticas principais
        "rodadas_ganhas": stats.rodadas_ganhas if stats else 0,
        "fichas_ganhas": stats.fichas_ganhas if stats else 0.0,
        "fichas_perdidas": stats.fichas_perdidas if stats else 0.0,
        "flushes": stats.flushes if stats else 0,
        "full_houses": stats.full_houses if stats else 0,

        # Extras lendários
        "sequencias": stats.sequencias if stats else 0,
        "quadras": stats.quadras if stats else 0,
        "straight_flushes": stats.straight_flushes if stats else 0,
        "royal_flushes": stats.royal_flushes if stats else 0,
        "torneios_vencidos": stats.torneios_vencidos if stats else 0,

        "maior_pote": stats.maior_pote if stats else 0.0,
        "vitorias": stats.vitorias if stats else 0,
        "rodadas_jogadas": stats.rodadas_jogadas if stats else 0,
        "mao_favorita": stats.mao_favorita if stats and stats.mao_favorita else None,
        "ranking_mensal": stats.ranking_mensal if stats else None,
        "vezes_no_top1": stats.vezes_no_top1 if stats else 0,
        "data_primeira_vitoria": stats.data_primeira_vitoria.isoformat() if stats and stats.data_primeira_vitoria else None,
        "data_ultima_vitoria": stats.data_ultima_vitoria.isoformat() if stats and stats.data_ultima_vitoria else None,
        "ultimo_update": stats.ultimo_update.isoformat() if stats and stats.ultimo_update else None
    }



# ==================== ROTA QUE PEGA O ID DO USUARIO PARA EXIBIR DADOS NO FRONT ====================
@router.get("/{id}")
def get_usuario_por_id(id: int, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    usuario = db.query(Usuario).filter(Usuario.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"id": usuario.id, "nome": usuario.nome, "email": usuario.email}







@router.get("/perfil/{user_id}", response_model=PerfilResponse)
def get_perfil_de_usuario(user_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    estatisticas = usuario.estatisticas

    if estatisticas is None:
        return PerfilResponse(
            id_publico=usuario.id_publico,
            nome=usuario.nome,
            avatar_url=usuario.avatar_url,
            rodadas_ganhas=0,
            rodadas_jogadas=0,
            fichas_ganhas=0.0,
            fichas_perdidas=0.0,
            sequencias=0,
            flushes=0,
            full_houses=0,
            quadras=0,
            straight_flushes=0,
            royal_flushes=0,
            torneios_vencidos=0,
            maior_pote=0.0,
            vitorias=0,
            mao_favorita=None,
            ranking_mensal=0,
            vezes_no_top1=0,
            data_primeira_vitoria=None,
            data_ultima_vitoria=None,
            ultimo_update=None
        )

    return PerfilResponse(
        id_publico=usuario.id_publico,
        nome=usuario.nome,
        avatar_url=usuario.avatar_url,
        rodadas_ganhas=estatisticas.rodadas_ganhas,
        rodadas_jogadas=estatisticas.rodadas_jogadas,
        fichas_ganhas=estatisticas.fichas_ganhas,
        fichas_perdidas=estatisticas.fichas_perdidas,
        sequencias=estatisticas.sequencias,
        flushes=estatisticas.flushes,
        full_houses=estatisticas.full_houses,
        quadras=estatisticas.quadras,
        straight_flushes=estatisticas.straight_flushes,
        royal_flushes=estatisticas.royal_flushes,
        torneios_vencidos=estatisticas.torneios_vencidos,
        maior_pote=estatisticas.maior_pote,
        vitorias=estatisticas.vitorias,
        mao_favorita=estatisticas.mao_favorita,
        ranking_mensal=estatisticas.ranking_mensal,
        vezes_no_top1=estatisticas.vezes_no_top1,
        data_primeira_vitoria=estatisticas.data_primeira_vitoria,
        data_ultima_vitoria=estatisticas.data_ultima_vitoria,
        ultimo_update=estatisticas.ultimo_update
    )

