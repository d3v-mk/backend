from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from panopoker.core.database import get_db
from panopoker.financeiro.models.pagamento import Pagamento
from panopoker.usuarios.models.usuario import Usuario
from panopoker.usuarios.models.promotor import Promotor
from panopoker.financeiro.utils.renovar_token_promoter_helper import renovar_token_do_promotor
from decimal import Decimal
import logging
import requests
import uuid
import asyncio

router = APIRouter(tags=["Webhook"])
logging.basicConfig(level=logging.INFO)

def calcular_liquido(valor: Decimal) -> Decimal:
    if valor <= Decimal("5"):
        margem = Decimal("0.20")
    elif valor <= Decimal("20"):
        margem = Decimal("0.40")
    else:
        margem = Decimal("0.60")
    return valor - margem

@router.post("/mercadopago")
async def webhook_mercado_pago(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    logging.info(f"📨 Webhook recebido: {payload}")

    if payload.get("type") != "payment":
        return {"status": "ignorado"}

    pagamento_id = str(payload["data"]["id"])
    logging.info(f"🔍 Buscando pagamento ID {pagamento_id}")

    # Retry: espera até 5 segundos pro pagamento aparecer
    pagamento = None
    for tentativa in range(5):
        pagamento = db.query(Pagamento).filter(Pagamento.payment_id == pagamento_id).first()
        if pagamento:
            break
        logging.warning(f"⏳ Tentativa {tentativa+1}/5: pagamento ainda não encontrado...")
        await asyncio.sleep(1)

    if not pagamento:
        logging.error(f"❌ Pagamento ID {pagamento_id} não encontrado após retries.")
        return {"status": "ignorado"}

    promotor = db.query(Promotor).filter(Promotor.id == pagamento.promotor_id).first()
    if not promotor or not promotor.access_token:
        logging.warning(f"❗ Promotor inválido ou sem token. ID: {pagamento.promotor_id}")
        return {"status": "ignorado"}

    headers = {"Authorization": f"Bearer {promotor.access_token}"}
    url = f"https://api.mercadopago.com/v1/payments/{pagamento_id}"

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 401:
            logging.warning("🔁 Token expirado, tentando renovar...")
            if renovar_token_do_promotor(promotor):
                db.commit()
                headers["Authorization"] = f"Bearer {promotor.access_token}"
                response = requests.get(url, headers=headers)
            else:
                logging.error("❌ Falha ao renovar token do promotor.")
                return {"status": "erro_token"}

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
                rake = valor_bruto - valor_liquido

                usuario.saldo += valor_liquido
                db.add(usuario)
                logging.info(f"✅ Fichas adicionadas: R${valor_liquido} para usuário ID {usuario.id}")

                metade_rake = rake / 2
                promotor.comissao_total = (promotor.comissao_total or Decimal("0")) + metade_rake
                promotor.saldo_repassar = (promotor.saldo_repassar or Decimal("0")) + metade_rake

                if promotor.saldo_repassar >= Decimal("5.00"):
                    promotor.bloqueado = True

                db.add(promotor)

            db.add(pagamento)
            db.commit()

    except Exception as e:
        logging.exception("❌ Erro ao processar pagamento via Mercado Pago.")

    return {"status": "ok"}
