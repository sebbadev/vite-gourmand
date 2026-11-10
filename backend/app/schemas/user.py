from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr
from app.models.entities import UserRole


class UserBase(BaseModel):
    """
    Attributs de base partagés pour les représentations utilisateurs.
    """
    email: EmailStr
    prenom: str
    nom: str
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    code_postal: Optional[str] = None
    ville: Optional[str] = None
    pays: Optional[str] = None
    role: UserRole


class UserResponse(UserBase):
    """
    Schéma de réponse pour exposer le profil utilisateur connecté.
    Hérite de UserBase et ajoute l'identifiant ainsi que les métadonnées techniques.
    Ne contient jamais le mot de passe haché (password_hash).
    """
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)