from pydantic_settings import BaseSettings
from typing import Set
from dotenv import load_dotenv
import os

load_dotenv(".env")

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://mking:Tangodown98@localhost:5432/panopoker" #migrar pro .env dps
    SECRET_KEY: str = "supersegredo_lendario"  # Trocar em produção e migrar pro .env dps
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 300

    # OAuth Google
    GOOGLE_WEB_CLIENT_ID: str
    GOOGLE_WEB_CLIENT_SECRET: str
    GOOGLE_ANDROID_CLIENT_ID: str
    GOOGLE_TOKEN_URL: str
    GOOGLE_REDIRECT_URI_WEB: str

    # Mercado Pago
    MERCADO_PAGO_ACCESS_TOKEN: str
    MERCADO_PAGO_CLIENT_SECRET: str
    MERCADO_PAGO_CLIENT_ID: str
    MERCADO_PAGO_REDIRECT_URI: str


    # E-mail
    EMAIL_DOMINIOS_VALIDOS_RAW: str = "[]"

    @property
    def EMAIL_DOMINIOS_VALIDOS(self) -> set[str]:
        import json
        try:
            return set(json.loads(self.EMAIL_DOMINIOS_VALIDOS_RAW))
        except Exception as e:
            raise ValueError(f"EMAIL_DOMINIOS_VALIDOS inválido: {e}")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
