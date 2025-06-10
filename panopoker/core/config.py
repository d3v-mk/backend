from pydantic_settings import BaseSettings
from pydantic import ConfigDict, computed_field, field_validator

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
    GOOGLE_REDIRECT_URI_WEB_DEV: str = "http://localhost:8000/auth/callback-web"

    # Mercado Pago
    MERCADO_PAGO_ACCESS_TOKEN: str
    MERCADO_PAGO_CLIENT_SECRET: str
    MERCADO_PAGO_CLIENT_ID: str
    MERCADO_PAGO_REDIRECT_URI: str
    MERCADO_PAGO_REDIRECT_URI_DEV: str = "http://localhost:8000/auth/callback-mp"

    # MiddleWare CORS
    SESSION_SECRET_KEY: str

    # Ativa e desativa modo producao
    IS_PRODUCTION: bool = False

    # E-mail
    EMAIL_DOMINIOS_VALIDOS_RAW: str = "[]"

    @computed_field(return_type=str)
    def GOOGLE_REDIRECT_URI_WEB_FINAL(self) -> str:
        return self.GOOGLE_REDIRECT_URI_WEB if self.IS_PRODUCTION else self.GOOGLE_REDIRECT_URI_WEB_DEV

    @computed_field(return_type=str)
    def MERCADO_PAGO_REDIRECT_URI_FINAL(self) -> str:
        return self.MERCADO_PAGO_REDIRECT_URI if self.IS_PRODUCTION else self.MERCADO_PAGO_REDIRECT_URI_DEV


    @property
    def EMAIL_DOMINIOS_VALIDOS(self) -> set[str]:
        import json
        try:
            return set(json.loads(self.EMAIL_DOMINIOS_VALIDOS_RAW))
        except Exception as e:
            raise ValueError(f"EMAIL_DOMINIOS_VALIDOS inválido: {e}")

    @computed_field(return_type=str)
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    @field_validator("IS_PRODUCTION", mode="before")
    def cast_bool(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes")
        return bool(v)

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow",
    )

settings = Settings()
