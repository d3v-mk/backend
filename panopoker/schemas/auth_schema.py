from pydantic import BaseModel



# === LOGIN DO APP ===
class LoginRequest(BaseModel):
    nome: str | None = None
    password: str | None = None
    id_token: str | None = None