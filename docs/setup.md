# ⚙️ Rodando

Passo a passo para rodar o projeto

---

## 📦 Requisitos

- 🐍 Python 3.10+
- 🐘 PostgreSQL rodando localmente (padrão: localhost:5432)

---

## ⚙️ Configurando o .env

Crie na raiz do projeto um arquivo .env assim:

- LIGA E DESLIGA MODO PRODUCAO
```bash
IS_PRODUCTION=false
```

- CONFIGURANDO O BANCO
```bash
DATABASE_USER=seu-usuario-psql
DATABASE_PASSWORD=sua-senha
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=panopoker
```

- MERCADO PAGO
```bash
MERCADO_PAGO_ACCESS_TOKEN=seu-acess-token
MERCADO_PAGO_CLIENT_SECRET=seu-client-secret
MERCADO_PAGO_CLIENT_ID=-seu-client-id
MERCADO_PAGO_REDIRECT_URI=https://api.yourdomain.com/auth/callback-mp
```

- GOOGLE CLIENT WEB
```bash
GOOGLE_WEB_CLIENT_ID=seu-client-id
GOOGLE_WEB_CLIENT_SECRET=seu-client-secret
```

- GOOGLE CLIENT ANDROID
```bash
GOOGLE_ANDROID_CLIENT_ID=seu-client-id
```

- AUTH LOGIN BOTAO GOOGLE PAINEL WEB
```bash
GOOGLE_TOKEN_URL=https://oauth2.googleapis.com/token
GOOGLE_REDIRECT_URI_WEB=https://api.yourdomain.com/auth/callback-web
```

- VALIDADORES DE DOMINIOS
```bash
EMAIL_DOMINIOS_VALIDOS_RAW=["gmail.com", "hotmail.com", "outlook.com", "yahoo.com"]
```

- CHAVE DO CORS
```bash
SESSION_SECRET_KEY=sua-secret-key
```

- CHAVE DA CONFIG
```bash
SECRET_KEY=sua-secret-key
```

> Existe um arquivo chamado geradordechaves.py onde voce pode gerar suas chaves do CORS e da config

---

## 🔌 Backend

- entra, cria novo ambiente venv/ativa, instala requirements
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

- roda o site e os paineis
```bash
uvicorn panopoker.main_site:app_site --host 0.0.0.0 --port 8000 --reload
```

- roda a API do jogo
```bash
uvicorn panopoker.main:app --host 0.0.0.0 --port 8080 --reload
```

---

## 🔑 Autenticação

O sistema suporta dois métodos de login:

- **Login com Google OAuth 2.0** (recomendado em produção)  
  Usuários autenticam via Google, recebendo um ID Token JWT validado pelo backend.

- **Login tradicional com usuário e senha (JWT)** (deprecated, modo dev)  
  Mantido para demonstração e testes locais, usando JWT customizado para sessões e bcrypt para hash de senha.

> Para rodar localmente, pode usar o login tradicional, mas em produção o foco é o login Google.

## 🔑 Configurando Login com Google

Para rodar o login Google localmente ou em produção, siga esses passos:

### 1. Criar Projeto no Google Cloud Console

- Acesse https://console.cloud.google.com/
- Crie um novo projeto ou use um existente
- Navegue em **APIs e Serviços > Credenciais**
- Crie uma **Tela de Consentimento OAuth** (público ou interno)
- Crie **IDs de Cliente OAuth 2.0**:
  - Tipo **Android**: registre o pacote do app + SHA1 do keystore
  - Tipo **Web**: registre o domínio do backend e a URL de callback (ex: `https://yourdomain.com/auth/callback-web`)

### 2. Variáveis de ambiente (.env)

Não esqueça de configurar as variáveis do google (configurando o .env)

---
