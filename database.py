# database.py
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 🚨 CAMBIO CLAVE: Usamos tu URL real de internet con el driver compatible de Vercel (+psycopg)
DATABASE_URL = "postgresql+psycopg://postgres_hehq_user:AIb893Z9jTGP6XyxTJKpuh9ppgj2c5I0@://render.com"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Definimos el modelo de la tabla en Postgres
class CartelLink(Base):
    __tablename__ = "links"
    id_cartel = Column(String, primary_key=True, index=True)
    url_destino = Column(String, nullable=False)

def inicializar_base_de_datos():
    # Crea la tabla automaticamente en el Postgres de Render
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
