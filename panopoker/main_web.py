from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from panopoker.site.router.listar_promotor import router as listar_promotor_router
from panopoker.site.router import login_web, painel_promotor, loja_promotor, configurar_loja, site_rank
from panopoker.usuarios.routers import admin

app_web = FastAPI()

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
