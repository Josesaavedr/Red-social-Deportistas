from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# Obtiene la URL de la base de datos de las variables de entorno.
# Asegúrate de que esta variable esté definida en el archivo docker-compose.yml.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./activities.db")

is_sqlite = "sqlite" in DATABASE_URL

# Controla si se muestran las sentencias SQL. Idealmente, 'False' en producción.
SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "False").lower() in ("true", "1", "t")

# Crea el motor de la base de datos.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if is_sqlite else {},
    echo=SQLALCHEMY_ECHO
)

# Configura la sesión de la base de datos.
# Esta clase creará nuevas sesiones de base de datos.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa para los modelos de SQLAlchemy
Base = declarative_base()

# Define la dependencia para la sesión de la base de datos.
# Esta función se usará en los endpoints de FastAPI para obtener una sesión de DB.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
