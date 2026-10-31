# database.py
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configura tus credenciales aca
DB_USER = "postgres"
DB_PASSWORD = "mati123"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "plancha_db"

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Definimos el modelo de la tabla en Postgres
class CartelLink(Base):
    __tablename__ = "links"
    id_cartel = Column(String, primary_key=True, index=True)
    url_destino = Column(String, nullable=False)

def inicializar_base_de_datos():
    # Crea la tabla automaticamente si no existe en Postgres
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
