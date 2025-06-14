from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from panopoker.site.routers import configurar_loja, loja_promotor, site_pages, login_web, painel_promotor, painel_admin
from panopoker.usuarios.routers import admin
from panopoker.core.config import settings

# Desativa tudo em producao para seguranca!!!
app_site = FastAPI(
    docs_url="/docs" if not settings.IS_PRODUCTION else None,
    redoc_url="/redoc" if not settings.IS_PRODUCTION else None,
    openapi_url="/openapi.json" if not settings.IS_PRODUCTION else None,
)

app_site.include_router(configurar_loja.router)
app_site.include_router(loja_promotor.router)
app_site.include_router(site_pages.router)
app_site.include_router(login_web.router)
app_site.include_router(painel_promotor.router)
app_site.include_router(painel_admin.router)
app_site.include_router(admin.router)

import pathlib
import os

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "panopoker" / "site" / "static"
app_site.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app_site.mount("/media", StaticFiles(directory=os.path.join("panopoker", "usuarios", "media")), name="media")
