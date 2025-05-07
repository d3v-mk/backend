from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from panopoker.core.config import settings  # Para pegar as configurações do banco de dados

DATABASE_URL = settings.DATABASE_URL  # Vamos buscar a URL do banco de dados nas configurações

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})  # Usado no SQLite
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Função para criar a conexão com o banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 👇 IMPORTA TODOS OS MODELOS EXPLICITAMENTE
import panopoker.usuarios.models.usuario
import panopoker.models.pagamento
import panopoker.models.mesa