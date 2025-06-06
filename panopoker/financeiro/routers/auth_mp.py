from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from panopoker.core.database import get_db
from panopoker.usuarios.models.usuario import Usuario
from panopoker.usuarios.models.promotor import Promotor
from panopoker.core.security import get_current_user_optional
from panopoker.core.config import settings
import requests

router = APIRouter()

@router.get("/auth/callback-mp")
def callback_oauth(
    code: str,
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user_optional)
):
    

    if not usuario or not usuario.is_promoter:
        raise HTTPException(status_code=403, detail="Usuário não autenticado ou não é promotor.")

    payload = {
        "grant_type": "authorization_code",
        "client_id": settings.MERCADO_PAGO_CLIENT_ID,
        "client_secret": settings.MERCADO_PAGO_CLIENT_SECRET,
        "code": code,
        "redirect_uri": settings.MERCADO_PAGO_REDIRECT_URI
    }

    response = requests.post("https://api.mercadopago.com/oauth/token", data=payload)
    if response.status_code != 200:
        return {"erro": "Falha ao trocar o code", "detalhes": response.json()}

    dados = response.json()
    access_token = dados["access_token"]
    refresh_token = dados["refresh_token"]
    mp_user_id = str(dados["user_id"])

    if not usuario.promotor:
        promotor = Promotor(
            user_id=usuario.id,
            user_id_mp=mp_user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            slug=f"promotor_{usuario.id}",
            nome=usuario.nome or "Loja do Promotor"
        )
        db.add(promotor)
    else:
        usuario.promotor.user_id_mp = mp_user_id
        usuario.promotor.access_token = access_token
        usuario.promotor.refresh_token = refresh_token
        if not usuario.promotor.slug:
            usuario.promotor.slug = f"promotor_{usuario.id}"

    db.commit()

    usuario.promotor = db.query(Promotor).filter(Promotor.user_id == usuario.id).first()

    return RedirectResponse(url="/loja/configurar", status_code=302)
