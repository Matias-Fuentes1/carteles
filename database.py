import os

from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import declarative_base, sessionmaker


# Obtener la conexión desde las variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "Falta configurar DATABASE_URL en las variables de entorno."
    )


# Adaptar la URL de Render al driver psycopg 3
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql+psycopg://",
        1
    )

elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1
    )

elif not DATABASE_URL.startswith("postgresql+psycopg://"):
    raise RuntimeError("El formato de DATABASE_URL no es válido.")


# Render requiere SSL para conexiones externas
if "sslmode=" not in DATABASE_URL:
    separator = "&" if "?" in DATABASE_URL else "?"
    DATABASE_URL += f"{separator}sslmode=require"


# Crear conexión
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=1,
    max_overflow=0
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# Modelo de la tabla
class CartelLink(Base):
    __tablename__ = "links"

    id_cartel = Column(String, primary_key=True, index=True)
    url_destino = Column(String, nullable=False)


# Crear tabla si todavía no existe
def inicializar_base_de_datos():
    Base.metadata.create_all(bind=engine)


# Sesión de base de datos
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
