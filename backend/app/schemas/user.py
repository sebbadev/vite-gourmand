from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr
from app.models.entities import UserRole


class UserResponse(BaseModel):
    """Schéma de réponse pour exposer le profil utilisateur connecté."""
    user_id: int
    email: EmailStr
    prenom: str
    nom: str
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    code_postal: Optional[str] = None
    ville: Optional[str] = None
    pays: Optional[str] = None
    role: UserRole
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)