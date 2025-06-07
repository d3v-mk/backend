from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import asyncio

from panopoker.core.database import engine, Base, SessionLocal
from panopoker.core import timers_async
from panopoker.core.config import settings

# Importa os modelos para garantir criação das tabelas
from panopoker.poker.financeiro.routers import saques
from panopoker.poker.models.mesa import Mesa, JogadorNaMesa
from panopoker.usuarios.models.usuario import Usuario
from panopoker.usuarios.models.promotor import Promotor

# Importa rotas backend
from panopoker.auth import login, register
from panopoker.financeiro.routers import webhook_mp, auth_mp
from panopoker.poker.routers import jogadores, mesa_cartas, mesa, loja_web_promoters
from panopoker.usuarios.routers import admin, usuario
from panopoker.lobby.routers import lobby
from panopoker.websocket import routes as ws_routes

import os
from fastapi.staticfiles import StaticFiles

# === Função de criação de tabelas e mesas ===
def create_tables():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.query(Mesa).first():
            mesas_definidas = (
                [
                    {"nome": f"Mesa Bronze {i + 1}", "buy_in": 0.30, "small_blind": 0.01, "big_blind": 0.02}
                    for i in range(5)
                ] +
                [
                    {"nome": f"Mesa Prata {i + 1}", "buy_in": 2.00, "small_blind": 0.05, "big_blind": 0.10}
                    for i in range(5)
                ] +
                [
                    {"nome": f"Mesa Ouro {i + 1}", "buy_in": 5.00, "small_blind": 0.10, "big_blind": 0.20}
                    for i in range(5)
                ]
            )

            for dados in mesas_definidas:
                if not db.query(Mesa).filter_by(nome=dados["nome"]).first():
                    nova_mesa = Mesa(
                        nome=dados["nome"],
                        buy_in=dados["buy_in"],
                        limite_jogadores=6,
                        small_blind=dados["small_blind"],
                        big_blind=dados["big_blind"],
                        cartas_comunitarias={}
                    )
                    db.add(nova_mesa)
            db.commit()
    finally:
        db.close()

# === Inicialização ===
create_tables()

# Desativa tudo em producao para seguranca!!!
app = FastAPI(
    docs_url="/docs" if not settings.IS_PRODUCTION else None,
    redoc_url="/redoc" if not settings.IS_PRODUCTION else None,
    openapi_url="/openapi.json" if not settings.IS_PRODUCTION else None,
)

app.mount(
    "/media",
    StaticFiles(directory=os.path.join("panopoker", "usuarios", "media")),
    name="media"
)

# Middleware CORS!
# Define se está em produção ou não
IS_PRODUCTION = os.getenv("IS_PRODUCTION", "false").lower() == "true"

if IS_PRODUCTION:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://www.panopoker.com",
            "https://api.panopoker.com"
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE", "PUT"],
        allow_headers=["Authorization", "Content-Type"],
    )
else:
    print("⚠️ Modo desenvolvimento: CORS liberado!")
    print("⚠️ Modo desenvolvimento: DOCS liberado!")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Middleware de sessão
secret_key = os.getenv("SESSION_SECRET_KEY")
if not secret_key:
    raise RuntimeError("🚨 SESSION_SECRET_KEY não definida no .env")

app.add_middleware(SessionMiddleware, secret_key=secret_key)


# Inclui as rotas backend
app.include_router(usuario.router)
app.include_router(webhook_mp.router)
app.include_router(saques.router)
app.include_router(mesa_cartas.router)
app.include_router(jogadores.router)
app.include_router(mesa.router)
app.include_router(admin.router)
app.include_router(login.router)
app.include_router(register.router)
app.include_router(auth_mp.router)
app.include_router(loja_web_promoters.router)
app.include_router(lobby.router)
app.include_router(ws_routes.router)

# Swagger personalizado
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="PanoPoker API",
        version="1.0.0",
        description="API do PanoPoker",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return openapi_schema

app.openapi = custom_openapi

# Loop principal para timers
timers_async.loop_principal = asyncio.get_event_loop()
