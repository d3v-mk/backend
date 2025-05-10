from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from panopoker.core.database import get_db
from panopoker.service.mercadopago import sdk
from panopoker.financeiro.models.pagamento import Pagamento
from panopoker.usuarios.models.usuario import Usuario
import logging

logging.basicConfig(level=logging.INFO)

router = APIRouter(prefix="/webhook", tags=["Webhook"])


@router.post("/mercadopago")
async def webhook_mercado_pago(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    logging.info(f"📨 Webhook recebido: {payload}")

    if payload.get("type") == "payment":
        pagamento_id = payload["data"]["id"]
        logging.info(f"🔍 Verificando pagamento ID {pagamento_id}")

        try:
            pagamento_info = sdk.payment().get(pagamento_id)["response"]
            status = pagamento_info.get("status")
            logging.info(f"💳 Status do pagamento: {status}")

            if status == "approved":
                pagamento = db.query(Pagamento).filter(Pagamento.payment_id == str(pagamento_id)).first()
                if pagamento and pagamento.status != "approved":
                    pagamento.status = "approved"

                    usuario = db.query(Usuario).filter(Usuario.id == pagamento.user_id).first()
                    if usuario:
                        usuario.saldo += pagamento.valor
                        db.add(usuario)

                    db.add(pagamento)
                    db.commit()
                    logging.info(f"✅ Fichas adicionadas para usuário ID {usuario.id}")

        except Exception as e:
            logging.exception("❌ Erro ao processar webhook do Mercado Pago")

    return {"status": "ok"}
