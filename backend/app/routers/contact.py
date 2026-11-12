from datetime import datetime, timezone
from typing import List
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.database import get_mongo_db
from app.core.deps import require_employe
from app.models.entities import Utilisateur
from app.schemas.contact import ContactCreate, ContactRead

router = APIRouter(tags=["Contact & Messagerie NoSQL"])


def _doc_to_contact_read(doc: dict) -> ContactRead:
    return ContactRead(
        id=str(doc["_id"]),
        nom=doc["nom"],
        prenom=doc["prenom"],
        email=doc["email"],
        telephone=doc.get("telephone"),
        objet=doc["objet"],
        message=doc["message"],
        traite=doc.get("traite", False),
        created_at=doc["created_at"],
    )


@router.post("/contact", response_model=ContactRead, status_code=status.HTTP_201_CREATED, summary="Envoi d'un message de contact (MongoDB)")
async def submit_contact_message(
    contact_in: ContactCreate,
    mongo = Depends(get_mongo_db)
):
    if not contact_in.rgpd_consent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le consentement au traitement des données personnelles (RGPD) est obligatoire."
        )

    doc = {
        "nom": contact_in.nom.strip(),
        "prenom": contact_in.prenom.strip(),
        "email": contact_in.email.lower().strip(),
        "telephone": contact_in.telephone,
        "objet": contact_in.objet.strip(),
        "message": contact_in.message.strip(),
        "traite": False,
        "created_at": datetime.now(timezone.utc),
    }

    result = await mongo.contacts.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _doc_to_contact_read(doc)


@router.get("/admin/contacts", response_model=List[ContactRead], summary="Liste des messages de contact (Employé / Admin)")
async def list_contact_messages(
    current_user: Utilisateur = Depends(require_employe),
    mongo = Depends(get_mongo_db)
):
    cursor = mongo.contacts.find().sort("created_at", -1)
    docs = await cursor.to_list(length=100)
    return [_doc_to_contact_read(d) for d in docs]


@router.patch("/admin/contacts/{contact_id}/traite", response_model=ContactRead, summary="Marquer un message comme traité")
async def mark_contact_treated(
    contact_id: str,
    current_user: Utilisateur = Depends(require_employe),
    mongo = Depends(get_mongo_db)
):
    if not ObjectId.is_valid(contact_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Identifiant de message invalide.")

    updated = await mongo.contacts.find_one_and_update(
        {"_id": ObjectId(contact_id)},
        {"$set": {"traite": True}},
        return_document=True
    )
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message introuvable.")

    return _doc_to_contact_read(updated)