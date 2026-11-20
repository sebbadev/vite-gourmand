from pathlib import Path
from functools import lru_cache
from typing import List, Union
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Résolution absolue du dossier backend/ (2 niveaux au-dessus de app/core/)
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE_PATH = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    # Métadonnées Application
    PROJECT_NAME: str = "Vite & Gourmand API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Sécurité & JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 heures

    # Configuration PostgreSQL
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = "vite_gourmand"

    # Configuration MongoDB
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB: str = "vite_gourmand_nosql"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:4200",
        "http://127.0.0.1:4200"
    ]

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Construit dynamiquement l'URL de connexion PostgreSQL pour SQLAlchemy avec psycopg2."""
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Chargement robuste du fichier .env via son chemin absolu
    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """Retourne une instance unique mise en cache des paramètres (Pattern Singleton)."""
    return Settings()


# Instance prête à être importée dans toute l'application
settings = get_settings()