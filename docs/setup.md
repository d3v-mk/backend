# ⚙️ Rodando

Passo a passo para rodar o projeto

---

## 📦 Requisitos

##### Obrigatorio:
- 🐍 Python 3.10+
- 🐘 PostgreSQL rodando localmente (padrão: localhost:5432)

---

## 🔌 Backend

- entra na pasta backend, cria novo ambiente venv, ativa e instala requirements
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

- roda o site e os paineis
```bash
uvicorn panopoker.main_site:app_site --host 0.0.0.0 --port 8000
```

- roda a API do jogo
```bash
uvicorn panopoker.main:app --host 0.0.0.0 --port 8080
```

---

## ⚙️ Configurando o .env

- Crie na raiz do projeto um arquivo .env assim:

```bash
# LIGA E DESLIGA MODO PRODUCAO
IS_PRODUCTION=false

# CONFIGURANDO O BANCO
DATABASE_USER=seu-usuario-psql
DATABASE_PASSWORD=sua-senha
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=panopoker

# MERCADO PAGO
MERCADO_PAGO_ACCESS_TOKEN=seu-acess-token
MERCADO_PAGO_CLIENT_SECRET=seu-client-secret
MERCADO_PAGO_CLIENT_ID=-seu-client-id
MERCADO_PAGO_REDIRECT_URI=https://api.yourdomain.com/auth/callback-mp
MERCADO_PAGO_REDIRECT_URI_DEV=http://localhost:8000/auth/callback-mp

# GOOGLE CLIENT WEB
GOOGLE_WEB_CLIENT_ID=seu-client-id
GOOGLE_WEB_CLIENT_SECRET=seu-client-secret
# GOOGLE CLIENT ANDROID
GOOGLE_ANDROID_CLIENT_ID=seu-client-id
# AUTH LOGIN BOTAO GOOGLE PAINEL WEB
GOOGLE_TOKEN_URL=https://oauth2.googleapis.com/token
GOOGLE_REDIRECT_URI_WEB=https://api.yourdomain.com/auth/callback-web
# SE FOR USAR LOGIN COM GOOGLE EM MODO DEV LEMBRE-SE DE CADASTRAR LOCALHOST NO CONSOLE DO GOOGLE!
GOOGLE_REDIRECT_URI_WEB_DEV=http://localhost:8000/auth/callback-web

# VALIDADORES DE DOMINIOS
EMAIL_DOMINIOS_VALIDOS_RAW=["gmail.com", "hotmail.com", "outlook.com", "yahoo.com"]

# CHAVE PARA ASSINAR COOKIES E TOKENS DE AUTENTICACAO
SESSION_SECRET_KEY=sua-secret-key

# CHAVE GLOBAL DE SEGURANCA DO APP
SECRET_KEY=sua-secret-key

# ALGORITMO JWT
ALGORITHM=HS256

# TEMPO DE EXPIRAÇÃO DO TOKEN EM MINUTOS
ACCESS_TOKEN_EXPIRE_MINUTES=300


```

> Existe um arquivo em `backend/panopoker/core/utils/geradordechaves.py` onde voce pode gerar suas KEYS

---

## 🐘 Configurando o banco

#### MacOS:
- Instale via terminal/brew:
```bash
brew install postgresql@15
```

- Starta o banco:
```bash
brew services start postgresql@15
```

- Entre no banco:
```bash
psql -U seu_user -d postgres
```

- Crie um novo banco com o nome panopoker
```sql
CREATE DATABASE panopoker;
```

#### Windows:

- Baixe o instalador oficial do PostgreSQL 15 aqui:
https://www.postgresql.org/download/windows/
Siga o instalador (ele já configura o serviço e cria usuário postgres)

- Starta o serviço (se não estiver rodando):
```bash
net start postgresql-x64-15
```

- Entre no banco pelo terminal do windows:
```bash
psql -U postgres -d postgres
```

- Crie o banco panopoker:
```sql
CREATE DATABASE panopoker;
```

#### Linux (Ubuntu/Debian):

- Instale o PostgreSQL 15:
```bash
sudo apt update
sudo apt install postgresql-15
```

- Starta o serviço:
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

- Troque pro usuário postgres e entre no psql:
```bash
sudo -i -u postgres
psql
```

- Crie o banco panopoker:
```sql
CREATE DATABASE panopoker;
```

---

## ⚙️ Configurando o MercadoPago

---

## 🔑 Autenticação

O sistema suporta dois métodos de login:

- **Login com Google OAuth 2.0** (recomendado em produção)  
  Usuários autenticam via Google, recebendo um ID Token JWT validado pelo backend.

- **Login tradicional com usuário e senha (JWT)** (deprecated/modo dev)  
  Mantido para demonstração e testes locais, usando JWT customizado para sessões e bcrypt para hash de senha.

> Para rodar localmente, pode usar o login tradicional, mas em produção o foco é o login Google.

## ⚙️ Configurando Login com Google

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

