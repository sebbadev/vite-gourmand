from typing import Optional
from pydantic import BaseModel, EmailStr, Field 
from app.models.entities import UserRole


class LoginRequest(BaseModel):
    """Schéma de validation des identifiants reçus lors de la connexion."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schéma de réponse contenant le jeton d'accès retourné au client."""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Structure des données embarquées (claims) dans le jeton JWT."""
    sub: str
    role: UserRole
    exp: int
    iat: Optional[int] = None


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    nouveau_password: str = Field(..., min_length=10, max_length=100)


class ChangePasswordRequest(BaseModel):
    ancien_password: str
    nouveau_password: str = Field(..., min_length=10, max_length=100)