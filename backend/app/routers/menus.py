from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.core.deps import require_employe
from app.models.entities import Menu, Plat, Theme, Regime, Allergene, Utilisateur
from app.schemas.menu import MenuListItem, MenuDetail, MenuCreate, MenuUpdate, CatalogueFilters, RefItem

router = APIRouter(prefix="/menus", tags=["Menus & Catalogue"])


@router.get(
    "/filtres",
    response_model=CatalogueFilters,
    summary="Récupère les référentiels pour alimenter les listes déroulantes du catalogue"
)
def get_catalogue_filters(db: Session = Depends(get_db)):
    """
    Retourne la liste complète des thèmes, régimes et allergènes enregistrés en base.
    Utilisé par Angular pour initialiser les filtres déroulants (dropdowns).
    """
    themes = db.execute(select(Theme).order_by(Theme.libelle)).scalars().all()
    regimes = db.execute(select(Regime).order_by(Regime.libelle)).scalars().all()
    allergenes = db.execute(select(Allergene).order_by(Allergene.libelle)).scalars().all()

    return CatalogueFilters(
        themes=[RefItem(id=t.theme_id, libelle=t.libelle) for t in themes],
        regimes=[RefItem(id=r.regime_id, libelle=r.libelle) for r in regimes],
        allergenes=[RefItem(id=a.allergene_id, libelle=a.libelle) for a in allergenes],
    )


@router.get(
    "",
    response_model=List[MenuListItem],
    summary="Catalogue public des menus avec filtres dynamiques"
)
def list_menus(
    prix_max: Optional[float] = Query(None, ge=0.0, description="Prix par personne maximum"),
    nb_personnes: Optional[int] = Query(None, ge=1, description="Capacité minimale demandée"),
    theme_id: Optional[int] = Query(None, description="Identifiant du thème événementiel"),
    regime_id: Optional[int] = Query(None, description="Identifiant du régime alimentaire (ex: Végétarien)"),
    sans_allergene_id: Optional[int] = Query(None, description="Exclure les menus contenant cet allergène"),
    db: Session = Depends(get_db)
):
    """
    Retourne la liste des menus actifs.
    Permet un filtrage multi-critères en temps réel pour le catalogue Angular.
    """
    stmt = (
        select(Menu)
        .where(Menu.is_active.is_(True), Menu.is_deleted.is_(False))
        .options(
            selectinload(Menu.themes),
            selectinload(Menu.plats).selectinload(Plat.allergenes),
            selectinload(Menu.plats).selectinload(Plat.regimes)
        )
    )

    if prix_max is not None:
        stmt = stmt.where(Menu.prix_par_personne <= prix_max)

    if nb_personnes is not None:
        stmt = stmt.where(Menu.nombre_personnes_min <= nb_personnes)

    if theme_id is not None:
        stmt = stmt.where(Menu.themes.any(Theme.theme_id == theme_id))

    if regime_id is not None:
        # Conformité stricte : tous les plats du menu doivent respecter le régime demandé
        stmt = stmt.where(
            Menu.plats.any(),
            ~Menu.plats.any(~Plat.regimes.any(Regime.regime_id == regime_id))
        )

    if sans_allergene_id is not None:
        # Exclusion stricte : aucun plat du menu ne doit comporter cet allergène
        stmt = stmt.where(~Menu.plats.any(Plat.allergenes.any(Allergene.allergene_id == sans_allergene_id)))

    menus = db.execute(stmt).scalars().all()

    result = []
    for m in menus:
        # Consolidation et déduplication des régimes et allergènes du menu
        regimes_dict = {}
        allergenes_dict = {}
        for p in m.plats:
            for r in p.regimes:
                regimes_dict[r.regime_id] = r.libelle
            for a in p.allergenes:
                allergenes_dict[a.allergene_id] = a.libelle

        themes_ref = [RefItem(id=t.theme_id, libelle=t.libelle) for t in m.themes]
        regimes_ref = [RefItem(id=rid, libelle=lib) for rid, lib in regimes_dict.items()]
        allergenes_ref = [RefItem(id=aid, libelle=lib) for aid, lib in allergenes_dict.items()]

        result.append(
            MenuListItem(
                menu_id=m.menu_id,
                titre=m.titre,
                nombre_personnes_min=m.nombre_personnes_min,
                prix_par_personne=m.prix_par_personne,
                description=m.description,
                quantite_disponible=m.quantite_disponible,
                images_url=m.images_url,
                is_active=m.is_active,
                themes=themes_ref,
                regimes=regimes_ref,
                allergenes=allergenes_ref
            )
        )
    return result


@router.get(
    "/{menu_id}",
    response_model=MenuDetail,
    summary="Fiche détaillée d'un menu avec composition et allergènes"
)
@router.get(
    "/{menu_id}",
    response_model=MenuDetail,
    summary="Fiche détaillée d'un menu avec composition et allergènes"
)
def get_menu_detail(
    menu_id: int,
    db: Session = Depends(get_db)
):
    """Retourne la fiche complète d'un menu pour l'affichage de détail et le panier."""
    stmt = (
        select(Menu)
        .where(Menu.menu_id == menu_id, Menu.is_deleted.is_(False))
        .options(
            selectinload(Menu.themes),
            selectinload(Menu.plats).selectinload(Plat.allergenes),
            selectinload(Menu.plats).selectinload(Plat.regimes),
            selectinload(Menu.plats).selectinload(Plat.themes)
        )
    )
    menu = db.execute(stmt).scalar_one_or_none()

    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu introuvable."
        )

    # 1. Structuration des plats et consolidation des régimes/allergènes du menu
    plats_dto = []
    menu_regimes = {}
    menu_allergenes = {}

    for p in menu.plats:
        for r in p.regimes:
            menu_regimes[r.regime_id] = r.libelle
        for a in p.allergenes:
            menu_allergenes[a.allergene_id] = a.libelle

        plats_dto.append({
            "plat_id": p.plat_id,
            "titre": p.titre,
            "type_de_plat": p.type_de_plat,
            "images_url": p.images_url,
            "allergenes": [{"id": a.allergene_id, "libelle": a.libelle} for a in p.allergenes],
            "regimes": [{"id": r.regime_id, "libelle": r.libelle} for r in p.regimes],
            "themes": [{"id": t.theme_id, "libelle": t.libelle} for t in p.themes],
        })

    return MenuDetail(
        menu_id=menu.menu_id,
        titre=menu.titre,
        nombre_personnes_min=menu.nombre_personnes_min,
        prix_par_personne=menu.prix_par_personne,
        description=menu.description,
        quantite_disponible=menu.quantite_disponible,
        images_url=menu.images_url,
        is_active=menu.is_active,
        created_at=menu.created_at,
        updated_at=menu.updated_at,
        themes=[{"id": t.theme_id, "libelle": t.libelle} for t in menu.themes],
        regimes=[{"id": rid, "libelle": lib} for rid, lib in menu_regimes.items()],
        allergenes=[{"id": aid, "libelle": lib} for aid, lib in menu_allergenes.items()],
        plats=plats_dto
    )


@router.post(
    "",
    response_model=MenuDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Création d'un menu (Réservé Employé & Admin)"
)
def create_menu(
    menu_in: MenuCreate,
    current_user: Utilisateur = Depends(require_employe),
    db: Session = Depends(get_db)
):
    """Crée un nouveau menu dans le catalogue et associe ses plats et thèmes."""
    new_menu = Menu(
        titre=menu_in.titre,
        nombre_personnes_min=menu_in.nombre_personnes_min,
        prix_par_personne=menu_in.prix_par_personne,
        description=menu_in.description,
        quantite_disponible=menu_in.quantite_disponible,
        images_url=menu_in.images_url,
        is_active=menu_in.is_active
    )

    if menu_in.plat_ids:
        plats = db.execute(select(Plat).where(Plat.plat_id.in_(menu_in.plat_ids))).scalars().all()
        new_menu.plats = list(plats)

    if menu_in.theme_ids:
        themes = db.execute(select(Theme).where(Theme.theme_id.in_(menu_in.theme_ids))).scalars().all()
        new_menu.themes = list(themes)

    db.add(new_menu)
    db.commit()
    db.refresh(new_menu)
    return get_menu_detail(new_menu.menu_id, db)


@router.delete(
    "/{menu_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Désactivation / Soft delete d'un menu (Réservé Employé & Admin)"
)
def delete_menu(
    menu_id: int,
    current_user: Utilisateur = Depends(require_employe),
    db: Session = Depends(get_db)
):
    """Effectue une suppression logique (is_deleted = True) pour conserver l'historique."""
    menu = db.execute(select(Menu).where(Menu.menu_id == menu_id)).scalar_one_or_none()
    if not menu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu introuvable.")

    menu.is_deleted = True
    menu.is_active = False
    db.commit()
    return None