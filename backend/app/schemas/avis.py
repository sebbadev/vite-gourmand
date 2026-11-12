from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.entities import ReviewStatus


class AvisNotes(BaseModel):
    qualite: int = Field(..., ge=1, le=5, description="Note de 1 à 5 sur la qualité culinaire")
    service: int = Field(..., ge=1, le=5, description="Note de 1 à 5 sur la ponctualité et le service")
    prix: int = Field(..., ge=1, le=5, description="Note de 1 à 5 sur le rapport qualité/prix")


class AvisCreate(AvisNotes):
    """Dépôt d'un avis client suite à une commande terminée."""
    description: str = Field(..., min_length=5, max_length=1000, description="Commentaire du client")


class AvisModerationUpdate(BaseModel):
    """Décision de modération par l'équipe (Approuvé ou Rejeté)."""
    statut: ReviewStatus


class AvisRead(BaseModel):
    """Représentation d'un document avis stocké dans MongoDB."""
    id: str
    commande_id: int
    numero_commande: Optional[str] = None
    user_id: int
    auteur_prenom: Optional[str] = None
    notes: AvisNotes
    note_moyenne: float
    description: str
    statut: str
    created_at: datetime