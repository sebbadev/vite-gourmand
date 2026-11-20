from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_admin
from app.core.security import get_password_hash
from app.models.entities import UserRole, Utilisateur
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/admin/employees", tags=["Administration - Gestion du Personnel"])


@router.get(
    "",
    response_model=List[UserResponse],
    summary="Liste des comptes employés (Admin uniquement)"
)
def list_employees(
    include_disabled: bool = True,
    current_user: Utilisateur = Depends(require_admin),
    db: Session = Depends(get_db)
):
    stmt = select(Utilisateur).where(Utilisateur.role == UserRole.EMPLOYE).order_by(Utilisateur.nom)
    if not include_disabled:
        stmt = stmt.where(Utilisateur.is_deleted.is_(False))
    return db.execute(stmt).scalars().all()


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Création d'un compte Employé par l'Administrateur"
)
def create_employee(
    user_in: UserCreate,
    current_user: Utilisateur = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Crée un compte collaborateur avec le rôle fixé obligatoirement à 'Employé'.
    Conformément au cahier des charges, aucun compte 'Administrateur' ne peut être créé via l'API.
    """
    email_clean = user_in.email.lower().strip()
    existing = db.execute(select(Utilisateur).where(Utilisateur.email == email_clean)).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette adresse email est déjà utilisée."
        )

    new_employee = Utilisateur(
        email=email_clean,
        password_hash=get_password_hash(user_in.password),
        prenom=user_in.prenom,
        nom=user_in.nom,
        telephone=user_in.telephone,
        adresse=user_in.adresse,
        code_postal=user_in.code_postal,
        ville=user_in.ville,
        pays=user_in.pays,
        role=UserRole.EMPLOYE,
    )

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee


@router.patch(
    "/{user_id}/disable",
    response_model=UserResponse,
    summary="Désactivation d'un compte Employé (Révocation d'accès)"
)
def disable_employee(
    user_id: int,
    current_user: Utilisateur = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Rend un compte employé immédiatement inutilisable via suppression logique (is_deleted = True)."""
    employee = db.execute(
        select(Utilisateur).where(Utilisateur.user_id == user_id, Utilisateur.role == UserRole.EMPLOYE)
    ).scalar_one_or_none()

    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compte employé introuvable.")

    employee.is_deleted = True
    db.commit()
    db.refresh(employee)
    return employee