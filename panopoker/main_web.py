from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from panopoker.site.routers.listar_promotor import router as listar_promotor_router
from panopoker.site.routers import login_web, painel_promotor, loja_promotor, configurar_loja, site_rank
from panopoker.usuarios.routers import admin
from panopoker.core.config import settings

app_web = FastAPI(
    docs_url="/docs" if not settings.IS_PRODUCTION else None,
    redoc_url="/redoc" if not settings.IS_PRODUCTION else None,
    openapi_url="/openapi.json" if not settings.IS_PRODUCTION else None,
)

app_web.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.panopoker.com", "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app_web.include_router(listar_promotor_router)
app_web.include_router(login_web.router)
app_web.include_router(admin.router)
app_web.include_router(painel_promotor.router)
app_web.include_router(loja_promotor.router)
app_web.include_router(configurar_loja.router)
app_web.include_router(site_rank.router)
