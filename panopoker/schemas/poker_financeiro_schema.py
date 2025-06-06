from pydantic import BaseModel
from decimal import Decimal

class ConfirmarSaqueRequest(BaseModel):
    valor_digitado: Decimal