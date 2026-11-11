from datetime import date, time, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

from app.models.entities import OrderStatus, PaymentStatus, Equipment, ContactMode


# --- Lignes de commande (Items / Détails) ---

class OrderItemCreate(BaseModel):
    """Ligne de commande envoyée par le client (menu et nombre de convives)."""
    menu_id: int
    quantite: int = Field(..., gt=0, description="Nombre de personnes pour ce menu")


class OrderDetailRead(BaseModel):
    """Détail d'une ligne de commande enregistrée."""
    detail_id: int
    menu_id: int
    menu_titre: Optional[str] = None
    quantite: int
    prix_applique: float

    model_config = ConfigDict(from_attributes=True)


# --- Simulation de devis (P3-04) ---

class QuoteRequest(BaseModel):
    """Demande de simulation de devis / calcul de panier."""
    items: List[OrderItemCreate] = Field(..., min_length=1, description="Liste des menus commandés")
    distance_km: float = Field(0.0, ge=0.0, description="Distance de livraison en km depuis le restaurant")


class QuoteResponse(BaseModel):
    """Résultat détaillé du calcul tarifaire selon les règles de gestion (RG)."""
    sous_total_brut: float = Field(..., description="Montant brut avant remises (RG-01)")
    remise_appliquee: float = Field(..., description="Montant total de la remise de 10% (RG-02)")
    sous_total_apres_remise: float = Field(..., description="Montant net des menus après remise")
    frais_livraison: float = Field(..., description="Frais forfaitaires et kilométriques (RG-03)")
    prix_total: float = Field(..., description="Prix final TTC à régler")
    eligible_remise: bool = Field(..., description="Indique si la remise volume a été activée")


class EquipmentPenaltyCheck(BaseModel):
    """Contrôle d'échéance de restitution du matériel (RG-04)."""
    date_prestation: date
    jours_ecoules: int
    depassement: bool
    penalite_forfaitaire: float = Field(600.0, description="Montant de la pénalité forfaitaire en euros")


# --- Passation et Consultation de Commande (P3-05) ---

class OrderCreate(BaseModel):
    """Payload pour créer une commande dans le tunnel d'achat."""
    date_prestation: date = Field(..., description="Date prévue de la prestation traiteur")
    heure_livraison: time = Field(..., description="Heure souhaitée de livraison (ex: 12:30:00)")
    adresse_livraison: str = Field(..., min_length=5, max_length=255, description="Adresse complète de livraison")
    distance_km: float = Field(0.0, ge=0.0, description="Distance kilométrique depuis le restaurant")
    items: List[OrderItemCreate] = Field(..., min_length=1, description="Liste des menus commandés")


class OrderRead(BaseModel):
    """Vue détaillée d'une commande pour le suivi client et l'espace employé."""
    commande_id: int
    numero_commande: str
    user_id: int
    date_prestation: date
    heure_livraison: time
    adresse_livraison: Optional[str] = None
    distance_km: float
    frais_livraison: float
    remise_appliquee: float
    prix_total: float
    statut: OrderStatus
    statut_paiement: PaymentStatus
    statut_materiel: Equipment
    date_commande: Optional[datetime] = None
    motif_annulation: Optional[str] = None
    mode_contact_annulation: Optional[ContactMode] = None
    contact_client_effectue: bool = False
    created_at: Optional[datetime] = None
    details: List[OrderDetailRead] = []

    model_config = ConfigDict(from_attributes=True)