from fastapi import HTTPException, APIRouter, Depends
from panopoker.core.database import get_db
from panopoker.core.security import Session
from sqlalchemy.orm import joinedload
from panopoker.usuarios.models.usuario import Usuario
from panopoker.usuarios.models.promotor import Promotor
from decimal import Decimal
from panopoker.core.security import get_current_user_required
from panopoker.financeiro.utils.renovar_token_promoter_helper import renovar_token_do_promotor
from time import time
import requests
import uuid
import random

router = APIRouter(prefix="/api")


@router.get("/loja/promotor/{slug}")
def get_promotor(slug: str, db: Session = Depends(get_db)):
    promotor = db.query(Promotor).options(joinedload(Promotor.usuario))\
        .filter(Promotor.slug == slug).first()
    if not promotor:
        raise HTTPException(status_code=404, detail="Promotor não encontrado")
    return {
        "nome": promotor.nome,
        "slug": promotor.slug,
        "avatar_url": promotor.usuario.avatar_url if promotor.usuario else "",
        "timestamp": int(time())
    }





@router.get("/gerar_pix/{slug}/{valor}")
def gerar_pix(slug: str, valor: Decimal,
              db: Session = Depends(get_db),
              usuario: Usuario = Depends(get_current_user_required)):  # troca aqui, obrigatório login

    promotor = db.query(Promotor).filter(Promotor.slug == slug).first()
    if not promotor or not promotor.access_token:
        raise HTTPException(status_code=404, detail="Promotor não encontrado ou sem token")

    # email garantido porque usuario é obrigatório aqui
    email = usuario.email

    # referencia única com id do usuário
    referencia = f"user_{usuario.id}_{uuid.uuid4()}"

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

