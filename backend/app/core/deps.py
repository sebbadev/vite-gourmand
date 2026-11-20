from typing import List
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.entities import Utilisateur, UserRole
from app.schemas.auth import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Utilisateur:
    """Valide le jeton JWT et extrait l'utilisateur en base de données."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides ou session expirée",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        role_str: str = payload.get("role")
        exp: int = payload.get("exp")

        if user_id is None or role_str is None:
            raise credentials_exception

        token_data = TokenPayload(sub=user_id, role=UserRole(role_str), exp=exp)
    except (jwt.PyJWTError, ValueError):
        raise credentials_exception

    stmt = select(Utilisateur).where(
        Utilisateur.user_id == int(token_data.sub),
        Utilisateur.is_deleted.is_(False)
    )
    user = db.execute(stmt).scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


class RoleChecker:
    """Contrôle d'accès basé sur les rôles (RBAC - Role-Based Access Control)."""
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: Utilisateur = Depends(get_current_user)) -> Utilisateur:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Droits insuffisants pour accéder à cette ressource"
            )
        return current_user


require_client = RoleChecker([UserRole.CLIENT, UserRole.EMPLOYE, UserRole.ADMIN])
require_employe = RoleChecker([UserRole.EMPLOYE, UserRole.ADMIN])
require_admin = RoleChecker([UserRole.ADMIN])