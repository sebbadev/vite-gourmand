from datetime import datetime, timezone
from typing import List, Optional
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db, get_mongo_db
from app.core.deps import require_client, require_employe
from app.models.entities import Commande, OrderStatus, ReviewStatus, Utilisateur
from app.schemas.avis import AvisCreate, AvisModerationUpdate, AvisNotes, AvisRead

router = APIRouter(tags=["Avis Clients & Modération NoSQL"])


def _doc_to_avis_read(doc: dict) -> AvisRead:
    notes = doc.get("notes", {"qualite": 5, "service": 5, "prix": 5})
    moyenne = round((notes["qualite"] + notes["service"] + notes["prix"]) / 3, 1)
    return AvisRead(
        id=str(doc["_id"]),
        commande_id=doc["commande_id"],
        numero_commande=doc.get("numero_commande"),
        user_id=doc["user_id"],
        auteur_prenom=doc.get("auteur_prenom"),
        notes=AvisNotes(**notes),
        note_moyenne=moyenne,
        description=doc["description"],
        statut=doc["statut"],
        created_at=doc["created_at"],
    )


@router.get("/avis", response_model=List[AvisRead], summary="Liste publique des avis clients approuvés")
async def list_public_avis(
    limit: int = Query(10, ge=1, le=50),
    mongo = Depends(get_mongo_db)
):
    """Retourne les avis modérés et approuvés pour la preuve sociale sur la page d'accueil."""
    cursor = mongo.avis.find({"statut": ReviewStatus.APPROVED.value}).sort("created_at", -1).limit(limit)
    docs = await cursor.to_list(length=limit)
    return [_doc_to_avis_read(d) for d in docs]


@router.post(
    "/commandes/{commande_id}/avis",
    response_model=AvisRead,
    status_code=status.HTTP_201_CREATED,
    summary="Déposer un avis suite à une commande terminée"
)
async def create_order_avis(
    commande_id: int,
    avis_in: AvisCreate,
    current_user: Utilisateur = Depends(require_client),
    db: Session = Depends(get_db),
    mongo = Depends(get_mongo_db)
):
    """
    Vérifie dans PostgreSQL que la commande appartient au client et est au statut 'Terminée',
    empêche les doublons, et insère l'avis dans MongoDB avec le statut initial 'En attente'.
    """
    commande = db.execute(
        select(Commande).where(Commande.commande_id == commande_id, Commande.is_deleted.is_(False))
    ).scalar_one_or_none()

    if not commande:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commande introuvable.")

    if commande.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cette commande ne vous appartient pas.")

    if commande.statut != OrderStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez évaluer qu'une commande au statut 'Terminée'."
        )

    existing_avis = await mongo.avis.find_one({"commande_id": commande_id, "user_id": current_user.user_id})
    if existing_avis:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un avis a déjà été déposé pour cette commande."
        )

    now = datetime.now(timezone.utc)
    doc = {
        "commande_id": commande.commande_id,
        "numero_commande": commande.numero_commande,
        "user_id": current_user.user_id,
        "auteur_prenom": current_user.prenom,
        "notes": {
            "qualite": avis_in.qualite,
            "service": avis_in.service,
            "prix": avis_in.prix,
        },
        "description": avis_in.description,
        "statut": ReviewStatus.PENDING.value,
        "created_at": now,
        "updated_at": now,
    }

    result = await mongo.avis.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _doc_to_avis_read(doc)


@router.get("/admin/avis", response_model=List[AvisRead], summary="Lister les avis pour modération (Employé / Admin)")
async def list_admin_avis(
    statut: Optional[ReviewStatus] = Query(ReviewStatus.PENDING, description="Filtrer par statut de modération"),
    current_user: Utilisateur = Depends(require_employe),
    mongo = Depends(get_mongo_db)
):
    query = {"statut": statut.value} if statut is not None else {}
    cursor = mongo.avis.find(query).sort("created_at", -1)
    docs = await cursor.to_list(length=100)
    return [_doc_to_avis_read(d) for d in docs]


@router.patch("/admin/avis/{avis_id}", response_model=AvisRead, summary="Approuver ou rejeter un avis (Employé / Admin)")
async def moderate_avis(
    avis_id: str,
    mod_in: AvisModerationUpdate,
    current_user: Utilisateur = Depends(require_employe),
    mongo = Depends(get_mongo_db)
):
    if not ObjectId.is_valid(avis_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Identifiant d'avis invalide.")

    oid = ObjectId(avis_id)
    updated = await mongo.avis.find_one_and_update(
        {"_id": oid},
        {"$set": {"statut": mod_in.statut.value, "updated_at": datetime.now(timezone.utc)}},
        return_document=True
    )

    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avis introuvable.")

    return _doc_to_avis_read(updated)