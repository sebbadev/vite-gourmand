from typing import List, Optional
from pydantic import BaseModel, Field


class GlobalKPIs(BaseModel):
    """Indicateurs financiers globaux calculés depuis la collection MongoDB commandes_stats."""
    nombre_commandes: int = Field(0, description="Nombre total de commandes terminées")
    ca_ht: float = Field(0.0, description="Chiffre d'affaires cumulé Hors Taxes")
    tva_collectee: float = Field(0.0, description="Montant cumulé de la TVA (10%)")
    ca_ttc: float = Field(0.0, description="Chiffre d'affaires cumulé Toutes Taxes Comprises")
    panier_moyen_ttc: float = Field(0.0, description="Panier moyen TTC par commande")
    total_remises: float = Field(0.0, description="Cumul des remises volume accordées (RG-02)")
    total_frais_livraison: float = Field(0.0, description="Cumul des frais kilométriques facturés (RG-03)")


class TopMenuStat(BaseModel):
    """Performance commerciale d'un menu (issu du $unwind sur le tableau menus)."""
    menu_id: int
    titre: str
    portions_vendues: int
    ca_genere_brut: float


class MonthlyRevenueStat(BaseModel):
    """Ventilation mensuelle du chiffre d'affaires."""
    annee: int
    mois: int
    nombre_commandes: int
    ca_ht: float
    ca_ttc: float


class AdminStatsResponse(BaseModel):
    """Réponse complète du tableau de bord décisionnel administrateur."""
    filtre_annee: Optional[int] = None
    kpis_globaux: GlobalKPIs
    top_menus: List[TopMenuStat] = []
    evolution_mensuelle: List[MonthlyRevenueStat] = []