from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session
import jwt
from app.core.security import decode_access_token
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import verify_password, create_access_token, get_password_hash
from app.models.entities import Utilisateur, UserRole
from app.schemas.auth import Token, ForgotPasswordRequest, ResetPasswordRequest, ChangePasswordRequest
from app.schemas.user import UserCreate, UserUpdate, UserResponse

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


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Inscription autonome d'un nouveau client"
)
def register_client(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Crée un nouveau compte utilisateur avec le rôle 'Client'.
    Vérifie l'unicité de l'adresse email et hache le mot de passe avec bcrypt.
    """
    existing = db.execute(
        select(Utilisateur).where(Utilisateur.email == user_in.email)
    ).scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette adresse email est déjà associée à un compte."
        )

    new_user = Utilisateur(
        email=user_in.email.lower().strip(),
        password_hash=get_password_hash(user_in.password),
        prenom=user_in.prenom,
        nom=user_in.nom,
        telephone=user_in.telephone,
        adresse=user_in.adresse,
        code_postal=user_in.code_postal,
        ville=user_in.ville,
        pays=user_in.pays,
        role=UserRole.CLIENT,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Mise à jour des coordonnées du profil connecté"
)
def update_my_profile(
    user_in: UserUpdate,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Permet à tout utilisateur connecté de mettre à jour ses informations personnelles."""
    update_data = user_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/forgot-password", summary="Demande de réinitialisation de mot de passe (anti-énumération)")
def forgot_password(
    payload: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Génère un jeton temporaire de 15 minutes si l'email existe.
    Retourne toujours 200 OK pour empêcher l'énumération des comptes.
    En environnement de développement, retourne le reset_token pour faciliter les tests.
    """
    user = db.execute(
        select(Utilisateur).where(
            Utilisateur.email == payload.email.lower().strip(),
            Utilisateur.is_deleted.is_(False)
        )
    ).scalar_one_or_none()

    response = {"message": "Si cette adresse email existe, un lien de réinitialisation a été envoyé."}

    if user:
        reset_token = create_access_token(
            subject=user.user_id,
            role="password_reset",
            expires_delta=timedelta(minutes=15)
        )
        # En mode dev/soutenance, on expose le jeton dans la réponse pour tester sans serveur SMTP
        response["dev_reset_token"] = reset_token

    return response


@router.post("/reset-password", summary="Validation du nouveau mot de passe via jeton temporaire")
def reset_password(
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    try:
        token_data = decode_access_token(payload.token)
        if token_data.get("role") != "password_reset":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Jeton invalide.")
        user_id = int(token_data.get("sub"))
    except (jwt.PyJWTError, ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lien expiré ou invalide.")

    user = db.execute(
        select(Utilisateur).where(Utilisateur.user_id == user_id, Utilisateur.is_deleted.is_(False))
    ).scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable.")

    user.password_hash = get_password_hash(payload.nouveau_password)
    db.commit()
    return {"message": "Mot de passe réinitialisé avec succès."}


@router.patch("/me/password", summary="Modification du mot de passe depuis l'espace personnel")
def change_my_password(
    payload: ChangePasswordRequest,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(payload.ancien_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le mot de passe actuel est incorrect."
        )

    current_user.password_hash = get_password_hash(payload.nouveau_password)
    db.commit()
    return {"message": "Mot de passe mis à jour avec succès."}