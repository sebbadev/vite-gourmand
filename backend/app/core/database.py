from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from motor.motor_asyncio import AsyncIOMotorClient
import certifi

from app.core.config import settings

# ---------------------------------------------------------------------------
# 1. PERSISTANCE RELATIONNELLE (PostgreSQL / SQLAlchemy)
# ---------------------------------------------------------------------------

# Moteur synchrone PostgreSQL
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,  # Vérifie la validité de la connexion avant exécution
    echo=settings.DEBUG  # Affiche les requêtes SQL en mode développement
)

# Fabrique de sessions transactionnelles
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Classe de base pour les entités ORM
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dépendance FastAPI fournissant une session SQLAlchemy par requête.
    Garantit la fermeture automatique de la connexion à la fin de l'appel HTTP.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# 2. PERSISTANCE ANALYTIQUE & MESSAGES (MongoDB / Motor)
# ---------------------------------------------------------------------------

ca = certifi.where()

mongo_client: AsyncIOMotorClient = AsyncIOMotorClient(
    settings.MONGO_URI,
    tls=True,
    tlsCAFile=ca,
    serverSelectionTimeoutMS=5000  # Évite d'attendre 30s en cas de souci
)
mongo_db = mongo_client[settings.MONGO_DB]


def get_mongo_db():
    """Dépendance FastAPI fournissant l'accès à la base MongoDB asynchrone."""
    return mongo_db