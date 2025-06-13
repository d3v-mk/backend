from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from panopoker.site.router.listar_promotor import router as listar_promotor_router
from panopoker.site.router import login_web
from panopoker.usuarios.routers import admin

app_web = FastAPI()

app_web.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app_web.include_router(listar_promotor_router)
app_web.include_router(login_web.router)
app_web.include_router(admin.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
