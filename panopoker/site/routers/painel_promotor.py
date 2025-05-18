from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from panopoker.core.database import get_db
from panopoker.usuarios.models.usuario import Usuario
from panopoker.financeiro.models.saque import Saque
from panopoker.core.security import get_current_user_optional
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import joinedload


router = APIRouter(prefix = "", tags= ["Painel Promotores"])
templates = Jinja2Templates(directory="panopoker/site/templates")  # ajusta se necessário

class SaqueCreate(BaseModel):
    jogador_id: int
    promotor_id: int
    valor: float

# ============= ENDPOINT QUE CAI NO PAINEL DO PROMOTOR ================
@router.get("/painel/promotor")
def painel_promotor(
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user_optional)
):
    if usuario is None or not usuario.is_promoter:
        return RedirectResponse("/", status_code=302)

    saques = db.query(Saque).options(joinedload(Saque.jogador)).filter(
        Saque.promotor_id == usuario.id
    ).all()

    return templates.TemplateResponse("painel_promotor.html", {
        "request": request,
        "saques": saques,
        "usuario": usuario,
        "saldo_repassar": 125.50,
        "comissao_total": 33.75
    })


# ================ ENDPOINT QUE CONCLUI O SAQUE DO JOGADOR ================
@router.post("/painel/promotor/concluir")
def concluir_saque_web(saque_id: int = Form(...), db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user_optional)):
    if not usuario.is_promoter:
        return RedirectResponse("/", status_code=302)

    saque = db.query(Saque).filter(Saque.id == saque_id, Saque.promotor_id == usuario.id).first()
    if saque and saque.status == "confirmado_pelo_jogador":
        saque.status = "concluido"
        db.commit()

    return RedirectResponse("/painel/promotor", status_code=302)

# ================ ENDPOINT QUE CRIA O SAQUE NO APP PRO JOGADOR ================
@router.post("/criar_saque")
def criar_saque(request: SaqueCreate, db: Session = Depends(get_db)):
    novo_saque = Saque(
        jogador_id=request.jogador_id,
        promotor_id=request.promotor_id,
        valor=request.valor,
        status="aguardando"
    )
    db.add(novo_saque)
    db.commit()
    return {"msg": "Saque criado"}

@router.post("/painel/promotor/solicitar_saque")
def solicitar_saque(
    request: Request,
    id_publico: str = Form(...),
    valor: float = Form(...),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user_optional)
):
    if not usuario or not usuario.is_promoter:
        return RedirectResponse(url="/login", status_code=302)

    jogador = db.query(Usuario).filter(Usuario.id_publico == id_publico).first()
    if not jogador:
        return HTMLResponse("Jogador não encontrado", status_code=404)

    saque = Saque(
        jogador_id=jogador.id,  # usa o ID real aqui, mas buscou com segurança
        promotor_id=usuario.id,
        valor=valor,
        status="aguardando",
        criado_em=datetime.utcnow()
    )
    db.add(saque)
    db.commit()
    return RedirectResponse(url="/painel/promotor", status_code=302)
