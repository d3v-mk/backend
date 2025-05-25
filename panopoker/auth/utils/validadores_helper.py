from fastapi import HTTPException
import re
from panopoker.core.config import EMAIL_DOMINIOS_VALIDOS


def verificar_email_valido(email: str):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise HTTPException(status_code=400, detail="Formato de email inválido.")

    dominio = email.split("@")[-1].lower()
    if dominio not in EMAIL_DOMINIOS_VALIDOS:
        raise HTTPException(status_code=400, detail="Domínio de email não permitido.")


def verificar_senha_forte(senha: str):
    if len(senha) < 8:
        raise HTTPException(status_code=400, detail="A senha deve ter no mínimo 8 caracteres.")
    if not re.search(r"[A-Z]", senha):
        raise HTTPException(status_code=400, detail="A senha deve conter pelo menos uma letra maiúscula.")
    if not re.search(r"[a-z]", senha):
        raise HTTPException(status_code=400, detail="A senha deve conter pelo menos uma letra minúscula.")
    if not re.search(r"\d", senha):
        raise HTTPException(status_code=400, detail="A senha deve conter pelo menos um número.")
    if not re.search(r"[!@#$%^&*()\-_=+[\]{};:,<.>/?\\|]", senha):
        raise HTTPException(status_code=400, detail="A senha deve conter pelo menos um símbolo.")
    
    senhas_proibidas = {"123456", "senha", "admin", "qwerty", "abcdef", "123123"}
    if senha.lower() in senhas_proibidas:
        raise HTTPException(status_code=400, detail="Essa senha é muito comum. Escolha outra.")

