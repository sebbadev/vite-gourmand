from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_employe
from app.models.entities import Horaire, Utilisateur
from app.schemas.horaire import HoraireRead, HoraireUpdate

router = APIRouter(prefix="/horaires", tags=["Horaires d'ouverture"])


@router.get("", response_model=List[HoraireRead], summary="Liste publique des horaires d'ouverture")
def list_horaires(db: Session = Depends(get_db)):
    stmt = select(Horaire).where(Horaire.is_deleted.is_(False)).order_by(Horaire.horaire_id.asc())
    return db.execute(stmt).scalars().all()


@router.put("/{horaire_id}", response_model=HoraireRead, summary="Modification d'une plage horaire (Employé / Admin)")
def update_horaire(
    horaire_id: int,
    horaire_in: HoraireUpdate,
    current_user: Utilisateur = Depends(require_employe),
    db: Session = Depends(get_db)
):
    horaire = db.execute(
        select(Horaire).where(Horaire.horaire_id == horaire_id, Horaire.is_deleted.is_(False))
    ).scalar_one_or_none()

    if not horaire:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jour introuvable.")

    if horaire_in.heure_ouverture >= horaire_in.heure_fermeture:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="L'heure d'ouverture doit être antérieure à l'heure de fermeture."
        )

    horaire.heure_ouverture = horaire_in.heure_ouverture
    horaire.heure_fermeture = horaire_in.heure_fermeture
    db.commit()
    db.refresh(horaire)
    return horaire