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
    logging.info(f"🔍 Buscando pagamento ID {pagamento_id} na API Mercado Pago")

    # 1. Busca promotor com token
    promotor = db.query(Promotor).filter(Promotor.access_token.isnot(None)).first()
    if not promotor:
        logging.warning("❗ Nenhum promotor com token disponível.")
        return {"status": "ignorado"}

    headers = {"Authorization": f"Bearer {promotor.access_token}"}
    url = f"https://api.mercadopago.com/v1/payments/{pagamento_id}"

    dados = None
    for tentativa in range(5):
        response = requests.get(url, headers=headers)
        if response.status_code == 401:
            logging.warning("🔁 Token expirado, tentando renovar...")
            if renovar_token_do_promotor(promotor):
                db.commit()
                headers["Authorization"] = f"Bearer {promotor.access_token}"
                continue
            else:
                logging.error("❌ Falha ao renovar token do promotor.")
                return {"status": "erro_token"}

        if response.status_code == 200:
            dados = response.json()
            break

        logging.warning(f"⏳ Tentativa {tentativa+1}/5: pagamento ainda não disponível na API...")
        await asyncio.sleep(1)

    if not dados:
        logging.error(f"❌ Pagamento ID {pagamento_id} não encontrado na API após retries.")
        return {"status": "ignorado"}

    status = dados.get("status")
    logging.info(f"💳 Status do pagamento: {status}")

    if status != "approved":
        return {"status": "ignorado"}

    # 2. Cria ou atualiza localmente pagamento
    pagamento = db.query(Pagamento).filter(Pagamento.payment_id == pagamento_id).first()
    if not pagamento:
        pagamento = Pagamento(
            payment_id=pagamento_id,
            status="approved",
            valor=Decimal(str(dados.get("transaction_amount"))),
            user_id=None,
            promotor_id=promotor.id,
        )
        db.add(pagamento)
    else:
        pagamento.status = "approved"

    # 3. Pega usuário pelo external_reference ou email (fallback)
    external_reference = dados.get("external_reference")
    usuario = None

    if external_reference and external_reference.startswith("user_"):
        try:
            user_id_str = external_reference.split("_")[1]
            user_id = int(user_id_str)
            usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
            logging.info(f"🔗 Usuário encontrado pelo external_reference: ID {user_id}")
        except Exception as e:
            logging.warning(f"⚠️ Erro ao interpretar external_reference: {external_reference} - {e}")

    if not usuario:
        email_pagador = dados.get("payer", {}).get("email")
        if email_pagador:
            usuario = db.query(Usuario).filter(Usuario.email == email_pagador).first()
            logging.info(f"🔗 Usuário encontrado pelo email: {email_pagador}")

    # 4. Atualiza saldo e comissões
    if usuario:
        pagamento.user_id = usuario.id
        valor_bruto = pagamento.valor
        valor_liquido = calcular_liquido(valor_bruto)
        rake = valor_bruto - valor_liquido

        usuario.saldo += valor_liquido
        promotor.comissao_total = (promotor.comissao_total or Decimal("0")) + rake / 2
        promotor.saldo_repassar = (promotor.saldo_repassar or Decimal("0")) + rake / 2

        if promotor.saldo_repassar >= Decimal("5.00"):
            promotor.bloqueado = True

        db.add(usuario)
        db.add(promotor)

        logging.info(f"✅ Fichas adicionadas: R${valor_liquido} para usuário {usuario.email}")

    db.commit()
    return {"status": "ok"}
