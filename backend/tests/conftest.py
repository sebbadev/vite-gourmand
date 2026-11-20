import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.security import create_access_token
from app.models.entities import UserRole


@pytest.fixture(scope="module")
def client():
    """Fournit un client HTTP synchrone pour tester l'application FastAPI."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def client_token_headers() -> dict:
    """En-tête d'authentification pour un utilisateur avec le rôle Client (user_id=3)."""
    token = create_access_token(subject=3, role=UserRole.CLIENT.value)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def employe_token_headers() -> dict:
    """En-tête d'authentification pour un utilisateur avec le rôle Employé (user_id=2)."""
    token = create_access_token(subject=2, role=UserRole.EMPLOYE.value)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_token_headers() -> dict:
    """En-tête d'authentification pour un utilisateur avec le rôle Administrateur (user_id=1)."""
    token = create_access_token(subject=1, role=UserRole.ADMIN.value)
    return {"Authorization": f"Bearer {token}"}