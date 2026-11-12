from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.models.entities import UserRole


class UserBase(BaseModel):
    """
    Attributs de base partagés pour les représentations utilisateurs.
    (Exclut volontairement 'role' et 'is_active' pour éviter toute élévation de privilèges à l'inscription).
    """
    email: EmailStr
    prenom: str = Field(..., min_length=2, max_length=50)
    nom: str = Field(..., min_length=2, max_length=50)
    telephone: Optional[str] = Field(None, max_length=20)
    adresse: Optional[str] = Field(None, max_length=255)
    code_postal: Optional[str] = Field(None, max_length=10)
    ville: Optional[str] = Field(None, max_length=50)
    pays: Optional[str] = Field(default="France", max_length=50)


class UserCreate(UserBase):
    """Payload d'inscription autonome d'un nouveau client."""
    password: str = Field(..., min_length=10, max_length=100, description="Mot de passe (8 caractères minimum)")


class UserUpdate(BaseModel):
    """Mise à jour partielle des coordonnées personnelles."""
    prenom: Optional[str] = Field(None, min_length=2, max_length=50)
    nom: Optional[str] = Field(None, min_length=2, max_length=50)
    telephone: Optional[str] = Field(None, max_length=20)
    adresse: Optional[str] = Field(None, max_length=255)
    code_postal: Optional[str] = Field(None, max_length=10)
    ville: Optional[str] = Field(None, max_length=50)
    pays: Optional[str] = Field(None, max_length=50)


class UserResponse(UserBase):
    """Représentation complète renvoyée par l'API (incluant le rôle en lecture seule)."""
    user_id: int
    role: UserRole
    is_deleted: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)