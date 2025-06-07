from pydantic_settings import BaseSettings
from pydantic import computed_field
from dotenv import load_dotenv

load_dotenv(".env")

class Settings(BaseSettings):
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str
    SECRET_KEY: str
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

    # MiddleWare CORS
    SESSION_SECRET_KEY: str

    # Ativa e desativa modo producao
    IS_PRODUCTION: bool = False

    # E-mail
    EMAIL_DOMINIOS_VALIDOS_RAW: str = "[]"

    @property
    def EMAIL_DOMINIOS_VALIDOS(self) -> set[str]:
        import json
        try:
            return set(json.loads(self.EMAIL_DOMINIOS_VALIDOS_RAW))
        except Exception as e:
            raise ValueError(f"EMAIL_DOMINIOS_VALIDOS inválido: {e}")

    @computed_field
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    model_config = {
        "case_sensitive": True,
        "env_file": ".env"
    }


settings = Settings()
