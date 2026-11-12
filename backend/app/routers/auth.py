from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import verify_password, create_access_token
from app.models.entities import Utilisateur
from app.schemas.auth import Token
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["Authentification"])


@router.post(
    "/login",
    response_model=Token,
    summary="Connexion utilisateur (Support polyvalent JSON & OAuth2 Form)"
)
async def login(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Authentification unifiée :
    1. Accepte le JSON pour le client Angular : { "email": "...", "password": "..." }
    2. Accepte le formulaire x-www-form-urlencoded pour Swagger UI (bouton Authorize).
    """
    content_type = request.headers.get("content-type", "").lower()

    email: Optional[str] = None
    password: Optional[str] = None

    if "application/json" in content_type:
        body = await request.json()
        email = body.get("email")
        password = body.get("password")
    elif "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        form = await request.form()
        # Dans le flux standard OAuth2 Password, l'identifiant est nommé 'username'
        email = form.get("username")
        password = form.get("password")
    else:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Type de contenu non supporté. Utilisez application/json ou application/x-www-form-urlencoded."
        )

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Identifiant et mot de passe requis."
        )

    # Recherche insensible à la casse
    email_clean = str(email).lower().strip()
    stmt = select(Utilisateur).where(
        Utilisateur.email == email_clean,
        Utilisateur.is_deleted.is_(False)
    )
    user = db.execute(stmt).scalar_one_or_none()

    if not user or not verify_password(str(password), user.password_hash):
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