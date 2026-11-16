from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_admin
from app.models.entities import Regime, Theme, Utilisateur
from app.schemas.menu import RefItem, RefItemPayload

router = APIRouter(prefix="/admin/referentiels", tags=["Administration - Référentiels"])


# --- RÉGIMES ALIMENTAIRES ---

@router.post("/regimes", response_model=RefItem, status_code=status.HTTP_201_CREATED, summary="Ajouter un régime alimentaire")
def create_regime(
    payload: RefItemPayload,
    current_user: Utilisateur = Depends(require_admin),
    db: Session = Depends(get_db)
):
    libelle_clean = payload.libelle.strip()
    existing = db.execute(select(Regime).where(Regime.libelle.ilike(libelle_clean))).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ce régime alimentaire existe déjà.")

    regime = Regime(libelle=libelle_clean)
    db.add(regime)
    db.commit()
    db.refresh(regime)
    return RefItem(id=regime.regime_id, libelle=regime.libelle)


@router.put("/regimes/{regime_id}", response_model=RefItem, summary="Modifier un régime alimentaire")
def update_regime(
    regime_id: int,
    payload: RefItemPayload,
    current_user: Utilisateur = Depends(require_admin),
    db: Session = Depends(get_db)
):
    regime = db.execute(select(Regime).where(Regime.regime_id == regime_id)).scalar_one_or_none()
    if not regime:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Régime introuvable.")

    regime.libelle = payload.libelle.strip()
    db.commit()
    db.refresh(regime)
    return RefItem(id=regime.regime_id, libelle=regime.libelle)


# --- THÈMES ÉVÉNEMENTIELS ---

@router.post("/themes", response_model=RefItem, status_code=status.HTTP_201_CREATED, summary="Ajouter un thème événementiel")
def create_theme(
    payload: RefItemPayload,
    current_user: Utilisateur = Depends(require_admin),
    db: Session = Depends(get_db)
):
    libelle_clean = payload.libelle.strip()
    existing = db.execute(select(Theme).where(Theme.libelle.ilike(libelle_clean))).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ce thème existe déjà.")

    theme = Theme(libelle=libelle_clean)
    db.add(theme)
    db.commit()
    db.refresh(theme)
    return RefItem(id=theme.theme_id, libelle=theme.libelle)


@router.put("/themes/{theme_id}", response_model=RefItem, summary="Modifier un thème événementiel")
def update_theme(
    theme_id: int,
    payload: RefItemPayload,
    current_user: Utilisateur = Depends(require_admin),
    db: Session = Depends(get_db)
):
    theme = db.execute(select(Theme).where(Theme.theme_id == theme_id)).scalar_one_or_none()
    if not theme:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thème introuvable.")

    theme.libelle = payload.libelle.strip()
    db.commit()
    db.refresh(theme)
    return RefItem(id=theme.theme_id, libelle=theme.libelle)