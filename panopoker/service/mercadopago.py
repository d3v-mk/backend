import mercadopago
import os
from dotenv import load_dotenv

# Carrega o .env se estiver usando
load_dotenv()

# Pega o token da variável de ambiente
ACCESS_TOKEN = os.getenv("MERCADO_PAGO_ACCESS_TOKEN")

if not ACCESS_TOKEN:
    raise ValueError("❌ Access Token do Mercado Pago não foi definido!")

sdk = mercadopago.SDK(ACCESS_TOKEN)

def criar_pagamento_pix(valor: float, email: str, nome: str):
    payment_data = {
        "transaction_amount": valor,
        "description": f"Compra de fichas no PanoPoker - R${valor:.2f}",
        "payment_method_id": "pix",
        "payer": {
            "email": email,
            "first_name": nome
        }
    }

    response = sdk.payment().create(payment_data)
    return response["response"]
