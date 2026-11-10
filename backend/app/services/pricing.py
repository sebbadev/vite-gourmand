from typing import List, Tuple
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Menu
from app.schemas.order import OrderItemCreate, QuoteResponse

# Constantes métier (RG-03 & RG-02)
FRAIS_LIVRAISON_BASE = 5.00       # Forfait fixe de base en euros
FRAIS_LIVRAISON_PAR_KM = 0.59     # Coût par kilomètre parcouru
TAUX_REMISE_VOLUME = 0.10         # 10% de remise
DELTA_SEUIL_REMISE = 5            # Nb personnes >= Min + 5


def calculate_delivery_cost(distance_km: float) -> float:
    """
    Règle de Gestion RG-03 :
    Frais de livraison = 5,00 € forfaitaires + 0,59 € par kilomètre parcouru.
    """
    if distance_km < 0:
        raise ValueError("La distance kilométrique ne peut pas être négative.")
    frais = FRAIS_LIVRAISON_BASE + (distance_km * FRAIS_LIVRAISON_PAR_KM)
    return round(frais, 2)


def calculate_menu_line(menu: Menu, quantite: int) -> Tuple[float, float, bool]:
    """
    Règles de Gestion RG-01 et RG-02 :
    - Vérifie que la quantité commandée respecte le seuil minimal du menu.
    - Applique 10% de remise si quantite >= nombre_personnes_min + 5.
    Retourne : (montant_brut, montant_remise, remise_activee)
    """
    # Validation de la contrainte plancher
    if quantite < menu.nombre_personnes_min:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Le menu '{menu.titre}' requiert un minimum de "
                f"{menu.nombre_personnes_min} personnes (demandé : {quantite})."
            )
        )

    montant_brut = round(quantite * menu.prix_par_personne, 2)
    remise = 0.0
    remise_activee = False

    # RG-02 : Remise de 10% si >= min + 5 personnes
    if quantite >= (menu.nombre_personnes_min + DELTA_SEUIL_REMISE):
        remise = round(montant_brut * TAUX_REMISE_VOLUME, 2)
        remise_activee = True

    return montant_brut, remise, remise_activee


def calculate_order_quote(
    items: List[OrderItemCreate],
    distance_km: float,
    db: Session
) -> QuoteResponse:
    """
    Agrège les lignes d'un devis/commande et produit la tarification globale :
    Sous-total brut, remises, frais kilométriques et total net à payer.
    """
    sous_total_brut = 0.0
    remise_totale = 0.0
    a_au_moins_une_remise = False

    for item in items:
        # Récupération du menu actif
        stmt = select(Menu).where(
            Menu.menu_id == item.menu_id,
            Menu.is_active.is_(True),
            Menu.is_deleted.is_(False)
        )
        menu = db.execute(stmt).scalar_one_or_none()
        if not menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Menu introuvable ou indisponible (ID: {item.menu_id})."
            )

        montant_brut, montant_remise, est_remise = calculate_menu_line(menu, item.quantite)
        sous_total_brut += montant_brut
        remise_totale += montant_remise
        if est_remise:
            a_au_moins_une_remise = True

    sous_total_apres_remise = round(sous_total_brut - remise_totale, 2)
    frais_livraison = calculate_delivery_cost(distance_km)
    prix_total = round(sous_total_apres_remise + frais_livraison, 2)

    return QuoteResponse(
        sous_total_brut=round(sous_total_brut, 2),
        remise_appliquee=round(remise_totale, 2),
        sous_total_apres_remise=sous_total_apres_remise,
        frais_livraison=frais_livraison,
        prix_total=prix_total,
        eligible_remise=a_au_moins_une_remise
    )