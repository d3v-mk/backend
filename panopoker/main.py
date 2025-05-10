from fastapi import FastAPI
from panopoker.core.database import engine, Base, SessionLocal
from fastapi.openapi.utils import get_openapi

# Importando os modelos para garantir que as tabelas sejam criadas no banco
from panopoker.poker.models.mesa import Mesa  # A tabela 'Mesa' será criada
from panopoker.usuarios.models.usuario import Usuario  # A tabela 'Usuario' será criada
from panopoker.poker.models.mesa import JogadorNaMesa # A tabela 'Jogadores_na_mesa' será criada



from fastapi.middleware.cors import CORSMiddleware


from panopoker.core import timers_async
import asyncio

from panopoker.usuarios.routers import usuario









# Criando as tabelas no banco de dados
# Isso garante que as tabelas serão criadas ao rodar a aplicação, se não existirem
def create_tables():
# Criando as tabelas no banco de dados
    Base.metadata.create_all(bind=engine)
    
    # Inserindo mesas predefinidas caso não existam
    db = SessionLocal()
    try:
        # Verifica se já existem mesas no banco de dados
        if not db.query(Mesa).first():
            mesas_definidas = [
                {
                    "nome": f"Mesa Bronze {i + 1}",
                    "buy_in": 0.30,
                    "small_blind": 0.01,
                    "big_blind": 0.02
                } for i in range(5)
            ] + [
                {
                    "nome": f"Mesa Prata {i + 1}",
                    "buy_in": 2.00,
                    "small_blind": 0.05,
                    "big_blind": 0.10
                } for i in range(5)
            ] + [
                {
                    "nome": f"Mesa Ouro {i + 1}",
                    "buy_in": 5.00,
                    "small_blind": 0.10,
                    "big_blind": 0.20
                } for i in range(5)
            ]

            for i, dados in enumerate(mesas_definidas):
                nome = dados["nome"]
                if not db.query(Mesa).filter_by(nome=nome).first():
                    nova_mesa = Mesa(
                        nome=nome,
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

# Rodando a criação das tabelas ao iniciar a aplicação (é chamado explicitamente)
create_tables()



# Criando a instância do FastAPI
app = FastAPI()

# Permite requisições de qualquer origem (dev only) // É PRA FUNCIONAR O PAINEL HTML DE TESTE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou restringe pra ["http://localhost"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Importar rotas
from panopoker.financeiro.routers import webhook, pagamentos

# Import do poker
from panopoker.poker.routers import acoes, jogadores, mesa_cartas, mesas_abertas, vez, mesa

from panopoker.usuarios.routers import admin

# Import do site
from fastapi.staticfiles import StaticFiles
from panopoker.site import site_pages

# Incluindo o roteador de usuários (rotas de autenticação e registro)
app.include_router(usuario.router)
app.include_router(webhook.router)
app.include_router(pagamentos.router)

# Rotas do poker
app.include_router(mesas_abertas.router)
app.include_router(mesa_cartas.router)
app.include_router(jogadores.router)
app.include_router(vez.router)
app.include_router(acoes.router)
app.include_router(mesa.router)
app.include_router(admin.router)

# Rotas do site
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import pathlib

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent  # backend/
STATIC_DIR = BASE_DIR / "panopoker" / "site" / "static"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(site_pages.router)



# Swagger JWT
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

timers_async.loop_principal = asyncio.get_event_loop()
