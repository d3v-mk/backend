from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
import pathlib
import os

from panopoker.core.database import engine, Base, SessionLocal
from panopoker.core import timers_async

# Importa os modelos para garantir criação das tabelas
from panopoker.poker.financeiro.routers import pagamentos, saques
from panopoker.poker.models.mesa import Mesa, JogadorNaMesa
from panopoker.usuarios.models.usuario import Usuario
from panopoker.usuarios.models.promotor import Promotor


# Importa rotas
from panopoker.auth import login, register
from panopoker.financeiro.routers import webhook_mp, auth_mp
from panopoker.poker.routers import acoes, jogadores, matchmaking, mesa_cartas, mesas_abertas, vez, mesa, loja_web_promoters
from panopoker.usuarios.routers import admin, usuario
from panopoker.site.routers import configurar_loja, loja_promotor, site_pages, login_web, painel_promotor

from panopoker.websocket import routes as ws_routes

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

app = FastAPI()

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de sessão
app.add_middleware(SessionMiddleware, secret_key="alguma_chave_segura_aqui")

# Inclui as rotas
app.include_router(usuario.router)
app.include_router(webhook_mp.router)
#app.include_router(pagamentos.router) poker/financeiro/pagamentos.py acho q ta inutil apagar se n sentir falta
app.include_router(saques.router)
app.include_router(mesas_abertas.router)
app.include_router(mesa_cartas.router)
app.include_router(matchmaking.router)
app.include_router(jogadores.router)
app.include_router(vez.router)
app.include_router(acoes.router)
app.include_router(mesa.router)
app.include_router(admin.router)
app.include_router(login.router)
app.include_router(register.router)
app.include_router(site_pages.router)
app.include_router(login_web.router)
app.include_router(painel_promotor.router)
app.include_router(loja_promotor.router)
app.include_router(auth_mp.router)
app.include_router(loja_web_promoters.router)
app.include_router(configurar_loja.router)


app.include_router(ws_routes.router)


# Static files do site
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "panopoker" / "site" / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# Media dos avatars
app.mount("/media", StaticFiles(directory=os.path.join("panopoker", "usuarios", "media")), name="media")

# Swagger JWT personalizado
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
