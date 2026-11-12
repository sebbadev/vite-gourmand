from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.entities import DishType


# --- Schémas Référentiels (Taxonomie) ---

class RefItem(BaseModel):
    """Représentation d'un allergène, régime ou thème."""
    id: int
    libelle: str

    model_config = ConfigDict(from_attributes=True)


# --- Schémas Plats ---

class PlatBase(BaseModel):
    titre: str = Field(..., max_length=50)
    type_de_plat: DishType
    images_url: Optional[str] = None


class PlatRead(PlatBase):
    plat_id: int
    allergenes: List[RefItem] = []
    regimes: List[RefItem] = []
    themes: List[RefItem] = []

    model_config = ConfigDict(from_attributes=True)


class PlatCreate(PlatBase):
    """Payload de création d'un plat avec ses associations taxonomiques."""
    allergene_ids: List[int] = Field(default=[], description="IDs des allergènes présents")
    regime_ids: List[int] = Field(default=[], description="IDs des régimes compatibles")
    theme_ids: List[int] = Field(default=[], description="IDs des thèmes associés")


class PlatUpdate(BaseModel):
    """Mise à jour partielle d'un plat."""
    titre: Optional[str] = Field(None, max_length=50)
    type_de_plat: Optional[DishType] = None
    images_url: Optional[str] = None
    allergene_ids: Optional[List[int]] = None
    regime_ids: Optional[List[int]] = None
    theme_ids: Optional[List[int]] = None
    

# --- Schémas Menus ---

class MenuBase(BaseModel):
    titre: str = Field(..., max_length=50)
    nombre_personnes_min: int = Field(..., gt=0)
    prix_par_personne: float = Field(..., gt=0.0)
    description: str
    quantite_disponible: int = Field(..., ge=0)
    images_url: str = Field(..., max_length=255)
    is_active: bool = True


class MenuCreate(MenuBase):
    """Payload pour créer un menu (associé à des plats et des thèmes)."""
    plat_ids: List[int] = Field(default=[], description="Liste des identifiants de plats à lier")
    theme_ids: List[int] = Field(default=[], description="Liste des identifiants de thèmes à lier")


class MenuUpdate(BaseModel):
    """Payload partiel pour mettre à jour un menu."""
    titre: Optional[str] = Field(None, max_length=50)
    nombre_personnes_min: Optional[int] = Field(None, gt=0)
    prix_par_personne: Optional[float] = Field(None, gt=0.0)
    description: Optional[str] = None
    quantite_disponible: Optional[int] = Field(None, ge=0)
    images_url: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None
    plat_ids: Optional[List[int]] = None
    theme_ids: Optional[List[int]] = None


class MenuListItem(BaseModel):
    """Vue allégée pour les cartes du catalogue public, avec métadonnées de filtrage."""
    menu_id: int
    titre: str
    nombre_personnes_min: int
    prix_par_personne: float
    description: str
    quantite_disponible: int
    images_url: str
    is_active: bool
    themes: List[RefItem] = []
    regimes: List[RefItem] = []      # Tous les régimes couverts par les plats du menu
    allergenes: List[RefItem] = []   # Tous les allergènes présents dans les plats du menu

    model_config = ConfigDict(from_attributes=True)


class MenuDetail(MenuBase):
    """Fiche complète d'un menu avec ses badges consolidés et ses plats."""
    menu_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    themes: List[RefItem] = []
    regimes: List[RefItem] = []       # Régimes consolidés du menu
    allergenes: List[RefItem] = []    # Allergènes consolidés du menu
    plats: List[PlatRead] = []

    model_config = ConfigDict(from_attributes=True)


class CatalogueFilters(BaseModel):
    """Structure des listes de référence pour alimenter les menus déroulants (dropdowns)."""
    themes: List[RefItem]
    regimes: List[RefItem]
    allergenes: List[RefItem]