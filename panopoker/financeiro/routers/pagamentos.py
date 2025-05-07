from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from panopoker.service.mercadopago import criar_pagamento_pix
from panopoker.core.database import get_db
from panopoker.core.security import get_current_user  # ajuste esse import se necessário
from pydantic import BaseModel
from panopoker.models.pagamento import Pagamento
import logging

router = APIRouter(prefix="/pagamentos", tags=["Pagamentos"])

class CompraRequest(BaseModel):
    valor: float

@router.post("/comprar_fichas")
def comprar_fichas(
    body: CompraRequest,
    db: Session = Depends(get_db),
    usuario = Depends(get_current_user)
):
    try:
        valor = body.valor

        if valor <= 0:
            raise HTTPException(status_code=400, detail="Valor inválido para compra.")

        pagamento = criar_pagamento_pix(valor, usuario.email, usuario.nome)

        if pagamento["status"] not in ["pending", "approved"]:
            raise HTTPException(status_code=400, detail="Erro ao criar pagamento.")

        novo_pagamento = Pagamento(
            user_id=usuario.id,
            valor=valor,
            status=pagamento["status"],
            payment_id=str(pagamento["id"]),
            qr_code=pagamento["point_of_interaction"]["transaction_data"]["qr_code"]
        )
        db.add(novo_pagamento)
        db.commit()

        return {
            "id": pagamento["id"],
            "status": pagamento["status"],
            "qr_code": pagamento["point_of_interaction"]["transaction_data"]["qr_code"],
            "qr_code_base64": pagamento["point_of_interaction"]["transaction_data"]["qr_code_base64"],
            "valor": pagamento["transaction_amount"],
            "descricao": pagamento["description"]
        }

    except Exception as e:
        logging.exception("Erro ao criar pagamento")
        raise HTTPException(status_code=500, detail="Erro interno ao gerar pagamento.")