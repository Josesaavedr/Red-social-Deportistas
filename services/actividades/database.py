# /services/actividades/database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configura la URL de la base de datos desde las variables de entorno.
# Si no se define, usará un archivo SQLite en el directorio local.
# En docker-compose.yml, esta variable apuntará a un servicio de base de datos.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./activities.db")

is_sqlite = "sqlite" in DATABASE_URL

# Controla si se muestran las sentencias SQL. Idealmente, 'False' en producción.
SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "False").lower() in ("true", "1", "t")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if is_sqlite else {},
    echo=SQLALCHEMY_ECHO
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependencia para obtener una sesión de base de datos en los endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()