from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./panopoker.db"
    SECRET_KEY: str = "123"  # Substitua com uma chave mais segura
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 300

settings = Settings()
