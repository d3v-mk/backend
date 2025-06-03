from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from panopoker.core.database import get_db
from fastapi import Depends
from fastapi.templating import Jinja2Templates
from panopoker.usuarios.models.usuario import Usuario
from panopoker.usuarios.models.promotor import Promotor
from sqlalchemy.orm import joinedload
from time import time
import requests
import uuid
import random
from decimal import Decimal
from panopoker.financeiro.utils.renovar_token_promoter_helper import renovar_token_do_promotor
from panopoker.core.security import get_current_user_optional, get_current_user, get_current_user_required


router = APIRouter(tags=["Loja Promotores"])
templates = Jinja2Templates(directory="panopoker/site/templates")


# ============================= LINK DA LOJA DO PROMOTOR =============================

@router.get("/loja/promotor/{slug}", response_class=HTMLResponse)
def loja_promotor(    slug: str,
    request: Request,
    db: Session = Depends(get_db),  # ← TEM que vir antes
    usuario: Usuario = Depends(get_current_user_required),
):
    promotor = db.query(Promotor)\
        .options(joinedload(Promotor.usuario))\
        .filter(Promotor.slug == slug).first()
    
    if not promotor:
        return HTMLResponse(
            content="<h1>Olá jogador!</h1><h1>Loja não encontrada</h1><h1>Verifique se o link está correto.</h1>",
            status_code=404
        )

    return templates.TemplateResponse("loja_promotor.html", {
        "request": request,
        "nome": promotor.nome,
        "slug": promotor.slug,
        "avatar_url": promotor.usuario.avatar_url if promotor.usuario else "",
        "timestamp": int(time()),
        # Nada de pix_copias aqui
    })

# ==================== GERA O PIX DINAMICO NA LOJA DO PROMOTOR ====================

@router.get("/api/gerar_pix/{slug}/{valor}")
def gerar_pix(slug: str, valor: Decimal,
              db: Session = Depends(get_db),
              usuario: Usuario | None = Depends(get_current_user_optional)):

    promotor = db.query(Promotor).filter(Promotor.slug == slug).first()
    if not promotor or not promotor.access_token:
        raise HTTPException(status_code=404, detail="Promotor não encontrado ou sem token")

    # Define email do pagador
    email = usuario.email if usuario else f"cliente.{slug}@servicosdigital.com"

    # Gera referência única com ID do usuário (se logado)
    if usuario:
        referencia = f"user_{usuario.id}"
    else:
        referencia = f"cliente_{slug}_{uuid.uuid4()}"

    # Descrições variadas
    descricoes_possiveis = [
        "Serviço digital contratado",
        "Cobrança por acesso online",
        "Assinatura de sistema virtual",
        "Produto digital adquirido",
        "Pagamento via plataforma"
    ]
    descricao = random.choice(descricoes_possiveis)

    payload = {
        "transaction_amount": float(valor),
        "description": descricao,
        "payment_method_id": "pix",
        "external_reference": referencia,
        "payer": {
            "email": email
        }
    }

    def gerar_headers(token: str):
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Idempotency-Key": str(uuid.uuid4())
        }

    headers = gerar_headers(promotor.access_token)
    url = "https://api.mercadopago.com/v1/payments"

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 401:
        print("⚠️ TOKEN EXPIRADO - Tentando renovar...")
        if renovar_token_do_promotor(promotor):
            db.commit()
            headers = gerar_headers(promotor.access_token)
            response = requests.post(url, json=payload, headers=headers)
        else:
            print("❌ Renovação falhou. Abortando.")
            raise HTTPException(status_code=500, detail="Erro ao renovar token do promotor")

    if response.status_code != 201:
        print("[ERRO MP]", response.status_code, response.json())
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar Pix: {response.json().get('message', 'Erro desconhecido')}"
        )

    dados = response.json()
    pix_code = dados["point_of_interaction"]["transaction_data"]["qr_code"]

    return {"pix_copia_cola": pix_code}
