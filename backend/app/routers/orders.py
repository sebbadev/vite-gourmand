from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.order import QuoteRequest, QuoteResponse
from app.services.pricing import calculate_order_quote

router = APIRouter(prefix="/commandes", tags=["Commandes & Devis"])


@router.post(
    "/devis",
    response_model=QuoteResponse,
    summary="Calcul automatique d'un devis panier (RG-01, RG-02, RG-03)"
)
def get_quote(
    quote_data: QuoteRequest,
    db: Session = Depends(get_db)
):
    """
    Simule le calcul d'une commande selon les règles de gestion :
    - RG-01 : Montant brut = Personnes x Prix unitaire (avec vérification seuil min)
    - RG-02 : 10% de remise si nb personnes >= min + 5
    - RG-03 : Frais de livraison = 5,00 € + 0,59 € / km
    """
    return calculate_order_quote(
        items=quote_data.items,
        distance_km=quote_data.distance_km,
        db=db
    )