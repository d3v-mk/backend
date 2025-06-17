uvicorn panopoker.main:app --host 0.0.0.0 --port 8080 --reload

uvicorn panopoker.main_web:app_web --host 0.0.0.0 --port 8000 --reload

uvicorn panopoker.main_site:app_site --host 0.0.0.0 --port 3000 --reload

npm run dev


# 📜 Documentação da VPS - panopoker.com

## 🧠 Informações Gerais

- **Sistema Operacional**: Ubuntu 22.04 LTS
- **Architecture:**: x86-64
- **Usuário Principal**: root
- **Gerenciador de Processos**: systemd
- **Firewall**: UFW
- **Certbot**: 0.40.0
- **Banco de dados**: PostgreSQL 12.22

---

## 📦 Pacotes Instalados

- apt-mark showmanual

```bash
apt-transport-https
base-files
base-passwd
bash
ca-certificates
certbot
cloud-init
curl
dash
diffutils
fail2ban
findutils
git
gnupg
grep
gzip
hostname
init
libdebconfclient0
libfwupdplugin1
libsodium23
libxmlb1
linux-generic
ncurses-base
ncurses-bin
net-tools
nginx
nodejs
openssh-server
postgresql
postgresql-contrib
python3-certbot-nginx
python3-nacl
python3-pymacaroons
python3-venv
python3.11
python3.11-dev
python3.11-venv
rep
screenfetch
software-properties-common
sysvinit-utils
tree
ubuntu-minimal
ubuntu-server
ubuntu-standard
xe-guest-utilities
```

## 📦 Pacotes Python Instalados

```bash
Package            Version
------------------ --------
alembic            1.14.1
annotated-types    0.7.0
anyio              4.6.2
APScheduler        3.11.0
attrs              23.2.0
Authlib            1.3.2
bcrypt             3.2.0
cachetools         5.3.3
certifi            2024.2.2
cffi               1.17.1
charset-normalizer 3.3.2
click              8.1.7
cryptography       42.0.5
dnspython          2.6.1
ecdsa              0.19.1
email_validator    2.2.0
fastapi            0.110.0
google-auth        2.29.0
greenlet           3.0.3
h11                0.14.0
httpcore           1.0.4
httpx              0.27.0
hypothesis         6.99.13
idna               3.6
iniconfig          2.0.0
itsdangerous       2.1.2
Jinja2             3.1.3
Mako               1.3.2
MarkupSafe         2.1.5
mercadopago        2.3.0
packaging          24.0
passlib            1.7.4
pillow             10.3.0
pip                24.0
psycopg2-binary    2.9.9
pyasn1             0.5.1
pyasn1-modules     0.3.0
pycparser          2.22
pydantic           2.6.4
pydantic_core      2.16.3
pydantic-settings  2.2.1
PyJWT              2.8.0
python-dotenv      1.0.1
python-jose        3.3.0
python-json-logger 2.0.7
python-multipart   0.0.9
requests           2.31.0
rsa                4.9
setuptools         69.2.0
six                1.16.0
sniffio            1.3.1
sortedcontainers   2.4.0
SQLAlchemy         2.0.29
starlette          0.36.3
typing_extensions  4.13.2
tzlocal            5.2
urllib3            2.2.1
uvicorn            0.29.0
websockets         11.0.3
```

## Node.js / NPM
- npm list -g --depth=0
```bash
/usr/lib
├── corepack@0.31.0
└── npm@10.8.2
```

---

## 🔧 Serviços Importantes

| Serviço                 | Porta      | Status | Observações                                                         |
| ----------------------- | ---------- | ------ | ------------------------------------------------------------------- |
| **Nginx**               | 80/443     | Ativo  | Web server + proxy reverso. Configs em `/etc/nginx/sites-available` |
| **PanoPoker API**       | 8080       | Ativo  | Backend com FastAPI (WebSocket + webhook). `panopoker-api.service`  |
| **PanoPoker Site**      | 3000 (int) | Ativo  | Frontend do site (Next.js). `panopoker-site.service`                |
| **PostgreSQL**          | 5432       | Ativo  | Banco de dados principal (versão 12)                                |
| **Fail2Ban**            | —          | Ativo  | Proteção contra brute-force no SSH e outros serviços                |
| **SSH (OpenSSH)**       | 2222       | Ativo  | Acesso remoto seguro via terminal (porta alterada)                  |
| **Unattended Upgrades** | —          | Ativo  | Atualizações automáticas de segurança                               |


#### 🔹 panopoker-site.service
- /etc/systemd/system/panopoker-site.service

```bash
[Unit]
Description=PanoPoker Web (Frontend + rotas site)
After=network.target

[Service]
User=root
WorkingDirectory=/root/backend
ExecStart=/root/backend/venv/bin/uvicorn panopoker.main_web:app_web --host 0.0.0.0 --port=8000 --no-server-header
Restart=always

[Install]
WantedBy=multi-user.target
root@vps59077:~# 
```
> 🔸 Observação: Este serviço roda o frontend + rotas do site no FastAPI, na porta 8000 internamente. É o “visual” do panopoker.com.

#### 🔹 panopoker-api.service
- /etc/systemd/system/panopoker-api.service

```bash
[Unit]
Description=PanoPoker API
After=network.target

[Service]
User=root
WorkingDirectory=/root/backend
EnvironmentFile=/root/backend/.env
ExecStart=/root/backend/venv/bin/uvicorn panopoker.main:app --host 0.0.0.0 --port 8080 --no-server-header
Restart=always

[Install]
WantedBy=multi-user.target
```

> 🔸 Observação: Este serviço roda a API principal com suporte a WebSocket e webhooks. Usa variáveis de ambiente do .env.


---

## ⚙️ Nginx

- tree
/etc/nginx/sites-available/
└── panopoker

```bash
# 🚨 Redireciona HTTP para HTTPS (site e API)
server {
    listen 80;
    server_name www.panopoker.com panopoker.com api.panopoker.com;

    # Força HTTPS com www para site
    if ($host = 'panopoker.com') {
        return 301 https://www.panopoker.com$request_uri;
    }

    # Força HTTPS para API
    if ($host = 'api.panopoker.com') {
        return 301 https://api.panopoker.com$request_uri;
    }

    return 301 https://$host$request_uri;
}

# 🔒 Redireciona panopoker.com (naked domain) para www
server {
    listen 443 ssl;
    server_name panopoker.com;

    ssl_certificate /etc/letsencrypt/live/panopoker.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/panopoker.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    return 301 https://www.panopoker.com$request_uri;
}

# 🌐 Site principal (React Build)
server {
    listen 443 ssl;
    server_name www.panopoker.com;

    ssl_certificate /etc/letsencrypt/live/panopoker.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/panopoker.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    root /var/www/panopoker;
    index index.html;

    # 👉 Tudo que for API vai pro backend
    location ^~ /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 👉 Todo o resto vai pro React
    location / {
        try_files $uri $uri/ /index.html;
    }
}

# 🚀 API (porta 8080)
server {
    listen 443 ssl;
    server_name api.panopoker.com;

    ssl_certificate /etc/letsencrypt/live/panopoker.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/panopoker.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {
        proxy_pass http://127.0.0.1:8080;  # 👈 API aqui!
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_read_timeout 86400;
    }
}
```

---

## deploy automatico front (vite/react)

- crie um arquivo `nano deploy_front.sh`
- salve, torne executavel com `chmod +x deploy_front.sh`
- execute `./deploy_front.sh`
```bash
#!/bin/bash

echo "🚀 Atualizando frontend do PanoPoker..."

cd /root/backend/web || exit

git pull origin main || exit

npm install

npm run build || exit

rm -rf /var/www/panopoker/*
cp -r dist/* /var/www/panopoker/

chown -R www-data:www-data /var/www/panopoker
nginx -t && systemctl reload nginx

echo "✅ Frontend atualizado com sucesso!"
```

---

## 🌐 Domínios

- **Principal**: www.panopoker.com
- **Subdomínios**: api.panopoker.com (WebSocket, webhook)

---

## 🔐 SSL (Let's Encrypt)

Certbot instalado via Snap.

Renovação automática configurada via cron ou systemd timer.

---

## 📁 Estrutura de Diretórios
- /var/www/panopoker/

Função: Diretório onde fica o build do frontend (React/Vite).
Origem dos arquivos: gerados com npm run build dentro do /root/backend/web
Atualização: via script de deploy (deploy_front.sh), que copia os arquivos da pasta dist/ pra cá.
Permissões: deve ser de propriedade do usuário www-data para que o Nginx consiga servir os arquivos corretamente.

---

## 🧪 Comandos Úteis

---

## 📋 Extras

---

🧙‍♂️ Documentado por: devmk  
📅 Atualizado em: 16/06/2025
