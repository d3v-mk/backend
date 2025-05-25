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
from panopoker.schemas.utils.helper_perfilresponse import build_perfil_response
@router.get("/perfil", response_model=PerfilResponse)
def get_perfil_completo(
    request: Request,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user)
):
    stats = db.query(EstatisticasJogador).filter_by(usuario_id=user.id).first()
    return build_perfil_response(user, stats, request)



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
    return build_perfil_response(usuario, estatisticas)