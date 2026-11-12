from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.core.deps import require_employe
from app.models.entities import Allergene, DishType, Plat, Regime, Theme, Utilisateur
from app.schemas.menu import PlatCreate, PlatRead, PlatUpdate, RefItem

router = APIRouter(prefix="/plats", tags=["Catalogue - Plats"])


def _serialize_plat(plat: Plat) -> PlatRead:
    return PlatRead(
        plat_id=plat.plat_id,
        titre=plat.titre,
        type_de_plat=plat.type_de_plat,
        images_url=plat.images_url,
        allergenes=[RefItem(id=a.allergene_id, libelle=a.libelle) for a in plat.allergenes],
        regimes=[RefItem(id=r.regime_id, libelle=r.libelle) for r in plat.regimes],
        themes=[RefItem(id=t.theme_id, libelle=t.libelle) for t in plat.themes],
    )


@router.get("", response_model=List[PlatRead], summary="Liste des plats du catalogue")
def list_plats(
    type_de_plat: Optional[DishType] = Query(None, description="Filtrer par catégorie (Entrée, Plat, Dessert)"),
    db: Session = Depends(get_db)
):
    stmt = (
        select(Plat)
        .options(
            selectinload(Plat.allergenes),
            selectinload(Plat.regimes),
            selectinload(Plat.themes),
        )
        .order_by(Plat.type_de_plat, Plat.titre)
    )
    if type_de_plat is not None:
        stmt = stmt.where(Plat.type_de_plat == type_de_plat)

    plats = db.execute(stmt).scalars().all()
    return [_serialize_plat(p) for p in plats]


@router.post(
    "",
    response_model=PlatRead,
    status_code=status.HTTP_201_CREATED,
    summary="Création d'un plat (Employé / Admin)"
)
def create_plat(
    plat_in: PlatCreate,
    current_user: Utilisateur = Depends(require_employe),
    db: Session = Depends(get_db)
):
    plat = Plat(
        titre=plat_in.titre,
        type_de_plat=plat_in.type_de_plat,
        images_url=plat_in.images_url,
    )
    if plat_in.allergene_ids:
        plat.allergenes = list(db.execute(select(Allergene).where(Allergene.allergene_id.in_(plat_in.allergene_ids))).scalars().all())
    if plat_in.regime_ids:
        plat.regimes = list(db.execute(select(Regime).where(Regime.regime_id.in_(plat_in.regime_ids))).scalars().all())
    if plat_in.theme_ids:
        plat.themes = list(db.execute(select(Theme).where(Theme.theme_id.in_(plat_in.theme_ids))).scalars().all())

    db.add(plat)
    db.commit()
    db.refresh(plat)
    return _serialize_plat(plat)


@router.put("/{plat_id}", response_model=PlatRead, summary="Modification d'un plat (Employé / Admin)")
def update_plat(
    plat_id: int,
    plat_in: PlatUpdate,
    current_user: Utilisateur = Depends(require_employe),
    db: Session = Depends(get_db)
):
    stmt = (
        select(Plat)
        .where(Plat.plat_id == plat_id)
        .options(selectinload(Plat.allergenes), selectinload(Plat.regimes), selectinload(Plat.themes))
    )
    plat = db.execute(stmt).scalar_one_or_none()
    if not plat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plat introuvable.")

    if plat_in.titre is not None:
        plat.titre = plat_in.titre
    if plat_in.type_de_plat is not None:
        plat.type_de_plat = plat_in.type_de_plat
    if plat_in.images_url is not None:
        plat.images_url = plat_in.images_url
    if plat_in.allergene_ids is not None:
        plat.allergenes = list(db.execute(select(Allergene).where(Allergene.allergene_id.in_(plat_in.allergene_ids))).scalars().all())
    if plat_in.regime_ids is not None:
        plat.regimes = list(db.execute(select(Regime).where(Regime.regime_id.in_(plat_in.regime_ids))).scalars().all())
    if plat_in.theme_ids is not None:
        plat.themes = list(db.execute(select(Theme).where(Theme.theme_id.in_(plat_in.theme_ids))).scalars().all())

    db.commit()
    db.refresh(plat)
    return _serialize_plat(plat)


@router.delete("/{plat_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Suppression d'un plat (Employé / Admin)")
def delete_plat(
    plat_id: int,
    current_user: Utilisateur = Depends(require_employe),
    db: Session = Depends(get_db)
):
    plat = db.execute(select(Plat).where(Plat.plat_id == plat_id)).scalar_one_or_none()
    if not plat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plat introuvable.")

    db.delete(plat)
    db.commit()
    return None