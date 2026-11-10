from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import verify_password, create_access_token
from app.models.entities import Utilisateur
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["Authentification"])


@router.post(
    "/login",
    response_model=Token,
    summary="Connexion utilisateur et émission du jeton JWT"
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Vérifie les identifiants et génère un jeton JWT d'accès.
    Retourne une erreur 401 générique en cas d'échec pour contrer l'énumération de comptes.
    """
    stmt = select(Utilisateur).where(
        Utilisateur.email == login_data.email.lower().strip(),
        Utilisateur.is_deleted.is_(False)
    )
    user = db.execute(stmt).scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        subject=user.user_id,
        role=user.role.value
    )

    return Token(access_token=access_token, token_type="bearer")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Récupération du profil utilisateur connecté"
)
def read_current_user_profile(
    current_user: Utilisateur = Depends(get_current_user)
):
    """Retourne les informations du compte actuellement authentifié."""
    return current_user