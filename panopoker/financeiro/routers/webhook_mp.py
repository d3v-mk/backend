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
                    valor_bruto = Decimal(str(pagamento.valor))
                    valor_liquido = calcular_liquido(valor_bruto)
                    rake = valor_bruto - valor_liquido  # Ex: 3.00 - 2.80 = 0.20

                    usuario.saldo += valor_liquido
                    db.add(usuario)
                    logging.info(f"✅ Fichas adicionadas: R${valor_liquido} para usuário ID {usuario.id}")

                    if promotor:
                        metade_rake = rake / 2  # 50% da rake
                        promotor.comissao_total = (promotor.comissao_total or Decimal("0")) + metade_rake
                        promotor.saldo_repassar = (promotor.saldo_repassar or Decimal("0")) + metade_rake

                        db.add(promotor)
                        logging.info(f"💰 Promotor ID {promotor.id}: comissão_total={promotor.comissao_total}, saldo_repassar (dívida contigo)={promotor.saldo_repassar}")

                    if promotor.saldo_repassar >= Decimal("5.00"):
                        promotor.bloqueado = True

                db.add(pagamento)
                db.commit()

        except Exception as e:
            logging.exception("❌ Erro ao consultar pagamento com token do promotor")

    return {"status": "ok"}