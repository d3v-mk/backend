# PanoPoker - Projeto de Casino Online

> Frontend integrados com FastAPI, React + TS, autenticação com cookies, painel Admin & Promotor.

---

## O que tem aqui?

- **Frontend React** com rotas protegidas para Admin, Promotor e Usuário comum.
- Autenticação via cookie HTTP-only.
- Painéis personalizados para Admin e Promotor.
- Sistema de atualização do usuário e proteção de rotas.
- Menu lateral estilizado e responsivo, tipo mini perfil.
- Controle de acesso detalhado para roles (admin/promotor/user).
- Deploy-ready (config pra produção já no projeto).

---

## Tecnologias

- Python 3.11+, FastAPI, SQLAlchemy
- React 18, TypeScript, React Router v6
- TailwindCSS
- Autenticação com cookies + API REST
- WebSocket (para o jogo, depois implementa)
- Git para versionamento

---

# ⚙️ Configurando o .env

- Faca na raiz do projeto (pasta web) um arquivo:
##### .env.development
```bash
VITE_API_URL=http://localhost:8000
```

- E outro:
##### .env.production
```bash
VITE_API_URL=https://www.yourdomain.com
```

---
## Como rodar local

1. Clone o repo:

\`\`\`bash
git clone https://github.com/d3v-mk/backend.git
cd backend
\`\`\`

2. Crie e ative seu ambiente virtual Python:

\`\`\`bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\\Scripts\\activate    # Windows
\`\`\`

3. Instale as dependências backend:

\`\`\`bash
pip install -r requirements.txt
\`\`\`

5. Rode o backend:

\`\`\`bash
uvicorn panopoker.main:app --reload
\`\`\`

6. No frontend (na pasta \`web\`):

\`\`\`bash
npm install
npm run dev
\`\`\`

---

## Rotas principais

- \`/login\` — Login do usuário
- \`/admin\` — Painel admin (só admins)
- \`/promotor\` — Painel promotor (só promotores)
- \`/me\` — Pega dados do usuário autenticado
- \`/logout\` — Logout
- \`/\` — Home pública

---

## Controle de acesso

- RotaPrivada: acessível a qualquer usuário logado.
- RotaAdmin: só admin.
- RotaPromotor: só promotor.
- Menu lateral exibe links conforme o perfil do usuário.

---

## Contato

Murilo Ferreira (devmk)
Email: devsoulmk@gmail.com
GitHub: [d3v-mk](https://github.com/d3v-mk)
