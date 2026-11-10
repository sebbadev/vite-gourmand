from datetime import date, time
from typing import Optional, List
from pydantic import BaseModel, Field


class OrderItemCreate(BaseModel):
    """Ligne de commande (menu et nombre de convives)."""
    menu_id: int
    quantite: int = Field(..., gt=0, description="Nombre de personnes pour ce menu")


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
    """Contrôle d'échéance de restitution du matériel."""
    date_prestation: date
    jours_ecoules: int
    depassement: bool
    penalite_forfaitaire: float = Field(600.0, description="Montant de la pénalité forfaitaire en euros")