import requests
import os
from panopoker.usuarios.models.promotor import Promotor


def renovar_token_do_promotor(promotor: Promotor) -> dict | None:
    print(f"🔁 Tentando renovar token do promotor ID {promotor.id}...")

    payload = {
        "grant_type": "refresh_token",
        "client_id": os.getenv("MERCADO_PAGO_CLIENT_ID"),
        "client_secret": os.getenv("MERCADO_PAGO_CLIENT_SECRET"),
        "refresh_token": promotor.refresh_token
    }

    try:
        response = requests.post("https://api.mercadopago.com/oauth/token", data=payload)
        print("📡 Resposta da renovação:", response.status_code, response.text)
        
        if response.status_code == 200:
            dados = response.json()
            promotor.access_token = dados["access_token"]
            promotor.refresh_token = dados["refresh_token"]
            print("✅ Token renovado com sucesso!")
            return dados
        else:
            print("[❌ MP] Erro ao renovar token:", response.status_code, response.text)
            return None
    except Exception as e:
        print("[🔥 EXCEPTION] Erro inesperado ao renovar token:", e)
        return None
