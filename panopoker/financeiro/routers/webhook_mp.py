from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from panopoker.core.database import get_db
from panopoker.financeiro.models.pagamento import Pagamento
from panopoker.usuarios.models.usuario import Usuario
from panopoker.core.security import get_current_user_optional
from panopoker.usuarios.models.promotor import Promotor
from panopoker.financeiro.utils.renovar_token_promoter_helper import renovar_token_do_promotor
from decimal import Decimal
import logging
import requests
import uuid
import random

logging.basicConfig(level=logging.INFO)

router = APIRouter(prefix="", tags=["Webhook"])

# ==================== WEBHOOK ====================

def calcular_liquido(valor: Decimal) -> Decimal:
    if valor <= Decimal("5"):
        margem = Decimal("0.20") #rake de 0.20
    elif valor <= Decimal("20"):
        margem = Decimal("0.40")# rake de 0.40
    else:
        margem = Decimal("0.60") # rake de 0.60 acima de 20
    return valor - margem

@router.post("/mercadopago")
async def webhook_mercado_pago(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    logging.info(f"📨 Webhook recebido: {payload}")

    if payload.get("type") == "payment":
        pagamento_id = str(payload["data"]["id"])
        logging.info(f"🔍 Verificando pagamento ID {pagamento_id}")

        pagamento = db.query(Pagamento).filter(Pagamento.payment_id == pagamento_id).first()
        if not pagamento:
            logging.warning(f"❗ Pagamento ID {pagamento_id} não encontrado.")
            return {"status": "ignorado"}

        promotor = db.query(Promotor).filter(Promotor.id == pagamento.promotor_id).first()
        if not promotor or not promotor.access_token:
            logging.warning(f"❗ Promotor não encontrado ou sem access_token.")
            return {"status": "ignorado"}

        headers = {
            "Authorization": f"Bearer {promotor.access_token}"
        }

        url = f"https://api.mercadopago.com/v1/payments/{pagamento_id}"

        try:
            response = requests.get(url, headers=headers)

            # 🔁 Se o token expirou, tenta renovar
            if response.status_code == 401:
                logging.warning("🔁 Access token expirado, tentando renovar...")
                if renovar_token_do_promotor(promotor):
                    db.commit()
                    headers["Authorization"] = f"Bearer {promotor.access_token}"
                    response = requests.get(url, headers=headers)
                else:
                    logging.error("❌ Falha ao renovar token.")
                    return {"status": "erro_renovacao"}

            response.raise_for_status()
            dados = response.json()
            status = dados.get("status")
            logging.info(f"💳 Status do pagamento: {status}")

            if status == "approved" and pagamento.status != "approved":
                pagamento.status = "approved"

                usuario = db.query(Usuario).filter(Usuario.id == pagamento.user_id).first()
                if usuario:
                    valor_liquido = calcular_liquido(Decimal(str(pagamento.valor)))  # <--- converte para Decimal
                    usuario.saldo += valor_liquido
                    db.add(usuario)
                    logging.info(f"✅ Fichas adicionadas: R${valor_liquido} para usuário ID {usuario.id}")

                db.add(pagamento)
                db.commit()

        except Exception as e:
            logging.exception("❌ Erro ao consultar pagamento com token do promotor")

    return {"status": "ok"}


# ==================== GERA O PIX DINAMICO NA LOJA DO PROMOTOR ====================

@router.get("/api/gerar_pix/{slug}/{valor}")
def gerar_pix(slug: str, valor: Decimal,  # <--- Valor já Decimal
              db: Session = Depends(get_db),
              usuario: Usuario | None = Depends(get_current_user_optional)):

    promotor = db.query(Promotor).filter(Promotor.slug == slug).first()
    if not promotor or not promotor.access_token:
        raise HTTPException(status_code=404, detail="Promotor não encontrado ou sem token")

    email = usuario.email if usuario else f"cliente.{slug}@servicosdigital.com"


    # 📃 Descrição com leve variação só pra não parecer clone
    descricoes_possiveis = [
        "Serviço digital contratado",
        "Cobrança por acesso online",
        "Assinatura de sistema virtual",
        "Produto digital adquirido",
        "Pagamento via plataforma"
    ]

    descricao = random.choice(descricoes_possiveis)

    payload = {
        "transaction_amount": float(valor),  # MercadoPago só aceita float na API deles, então só aqui converte pra float!
        "description": descricao,
        "payment_method_id": "pix",
        "external_reference": f"pedido_{uuid.uuid4()}",
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

    # 🔁 Se o token expirou, tenta renovar e refazer
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
