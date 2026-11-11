from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.core.deps import get_current_user, require_client
from app.models.entities import (
    Commande,
    CommandeDetail,
    Menu,
    Utilisateur,
    UserRole,
    OrderStatus,
    PaymentStatus,
    Equipment,
)
from app.schemas.order import (
    QuoteRequest,
    QuoteResponse,
    OrderCreate,
    OrderRead,
    OrderDetailRead,
)
from app.services.pricing import calculate_order_quote

router = APIRouter(prefix="/commandes", tags=["Commandes & Devis"])


def generate_order_number(db: Session) -> str:
    """
    Génère un identifiant de commande lisible et unique : CMD-AAAA-XXXX.
    Exemple : CMD-2026-0004.
    """
    current_year = datetime.now().year
    prefix = f"CMD-{current_year}-"

    # Compter le nombre de commandes de l'année pour le séquentiel
    count_stmt = select(func.count(Commande.commande_id)).where(
        Commande.numero_commande.like(f"{prefix}%")
    )
    total_year = db.execute(count_stmt).scalar() or 0
    sequence_num = total_year + 1
    return f"{prefix}{sequence_num:04d}"


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


@router.post(
    "",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
    summary="Passation d'une commande ferme par un client"
)
def create_order(
    order_in: OrderCreate,
    current_user: Utilisateur = Depends(require_client),
    db: Session = Depends(get_db)
):
    """
    Crée une commande client :
    - Valide les seuils minimaux et les stocks disponibles
    - Décrémente les stocks de chaque menu
    - Fige les prix avec remises et frais kilométriques (RG-01, RG-02, RG-03)
    - Initialise le statut à 'En attente de validation'
    """
    # 1. Calculer la tarification exacte via le moteur de pricing
    quote = calculate_order_quote(
        items=order_in.items,
        distance_km=order_in.distance_km,
        db=db
    )

    # 2. Vérifier et décrémenter les stocks de menus
    menus_cache = {}
    for item in order_in.items:
        stmt = select(Menu).where(
            Menu.menu_id == item.menu_id,
            Menu.is_active.is_(True),
            Menu.is_deleted.is_(False)
        )
        menu = db.execute(stmt).scalar_one_or_none()
        if not menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Menu ID {item.menu_id} introuvable."
            )

        if menu.quantite_disponible < item.quantite:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Stock insuffisant pour le menu '{menu.titre}'. "
                    f"Disponible : {menu.quantite_disponible}, demandé : {item.quantite}."
                )
            )

        # Décrémentation du stock
        menu.quantite_disponible -= item.quantite
        menus_cache[item.menu_id] = menu

    # 3. Création de l'entité Commande
    numero = generate_order_number(db)
    new_order = Commande(
        numero_commande=numero,
        user_id=current_user.user_id,
        date_prestation=order_in.date_prestation,
        heure_livraison=order_in.heure_livraison,
        adresse_livraison=order_in.adresse_livraison,
        distance_km=order_in.distance_km,
        frais_livraison=quote.frais_livraison,
        remise_appliquee=quote.remise_appliquee,
        prix_total=quote.prix_total,
        statut=OrderStatus.PENDING,
        statut_paiement=PaymentStatus.DUE,
        statut_materiel=Equipment.INCLUDED
    )
    db.add(new_order)
    db.flush()  # Récupérer new_order.commande_id

    # 4. Enregistrement des lignes de commande avec prix unitaire figé
    for item in order_in.items:
        m = menus_cache[item.menu_id]
        detail = CommandeDetail(
            commande_id=new_order.commande_id,
            menu_id=m.menu_id,
            quantite=item.quantite,
            prix_applique=m.prix_par_personne
        )
        db.add(detail)

    db.commit()
    db.refresh(new_order)

    # Structuration de la réponse DTO
    details_dto = [
        OrderDetailRead(
            detail_id=d.detail_id,
            menu_id=d.menu_id,
            menu_titre=menus_cache[d.menu_id].titre,
            quantite=d.quantite,
            prix_applique=d.prix_applique
        )
        for d in new_order.details
    ]

    return OrderRead(
        commande_id=new_order.commande_id,
        numero_commande=new_order.numero_commande,
        user_id=new_order.user_id,
        date_prestation=new_order.date_prestation,
        heure_livraison=new_order.heure_livraison,
        adresse_livraison=new_order.adresse_livraison,
        distance_km=new_order.distance_km,
        frais_livraison=new_order.frais_livraison,
        remise_appliquee=new_order.remise_appliquee,
        prix_total=new_order.prix_total,
        statut=new_order.statut,
        statut_paiement=new_order.statut_paiement,
        statut_materiel=new_order.statut_materiel,
        date_commande=new_order.date_commande,
        created_at=new_order.created_at,
        details=details_dto
    )


@router.get(
    "/me",
    response_model=List[OrderRead],
    summary="Historique des commandes du client connecté"
)
def get_my_orders(
    current_user: Utilisateur = Depends(require_client),
    db: Session = Depends(get_db)
):
    """Retourne la liste des commandes passées par l'utilisateur connecté."""
    stmt = (
        select(Commande)
        .where(Commande.user_id == current_user.user_id, Commande.is_deleted.is_(False))
        .options(selectinload(Commande.details).selectinload(CommandeDetail.menu))
        .order_by(Commande.date_commande.desc())
    )
    commandes = db.execute(stmt).scalars().all()

    result = []
    for c in commandes:
        details_dto = [
            OrderDetailRead(
                detail_id=d.detail_id,
                menu_id=d.menu_id,
                menu_titre=d.menu.titre if d.menu else "Menu archivé",
                quantite=d.quantite,
                prix_applique=d.prix_applique
            )
            for d in c.details
        ]
        result.append(
            OrderRead(
                commande_id=c.commande_id,
                numero_commande=c.numero_commande,
                user_id=c.user_id,
                date_prestation=c.date_prestation,
                heure_livraison=c.heure_livraison,
                adresse_livraison=c.adresse_livraison,
                distance_km=c.distance_km,
                frais_livraison=c.frais_livraison,
                remise_appliquee=c.remise_appliquee,
                prix_total=c.prix_total,
                statut=c.statut,
                statut_paiement=c.statut_paiement,
                statut_materiel=c.statut_materiel,
                date_commande=c.date_commande,
                motif_annulation=c.motif_annulation,
                mode_contact_annulation=c.mode_contact_annulation,
                contact_client_effectue=c.contact_client_effectue,
                created_at=c.created_at,
                details=details_dto
            )
        )
    return result


@router.get(
    "/{commande_id}",
    response_model=OrderRead,
    summary="Suivi détaillé d'une commande par identifiant"
)
def get_order_detail(
    commande_id: int,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Consulte le suivi d'une commande.
    Un client ne peut consulter que ses propres commandes.
    Les employés et administrateurs ont accès à toutes les commandes.
    """
    stmt = (
        select(Commande)
        .where(Commande.commande_id == commande_id, Commande.is_deleted.is_(False))
        .options(selectinload(Commande.details).selectinload(CommandeDetail.menu))
    )
    commande = db.execute(stmt).scalar_one_or_none()

    if not commande:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commande introuvable."
        )

    # Contrôle de sécurité (cloisonnement client)
    if current_user.role == UserRole.CLIENT and commande.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé à cette commande."
        )

    details_dto = [
        OrderDetailRead(
            detail_id=d.detail_id,
            menu_id=d.menu_id,
            menu_titre=d.menu.titre if d.menu else "Menu archivé",
            quantite=d.quantite,
            prix_applique=d.prix_applique
        )
        for d in commande.details
    ]

    return OrderRead(
        commande_id=commande.commande_id,
        numero_commande=commande.numero_commande,
        user_id=commande.user_id,
        date_prestation=commande.date_prestation,
        heure_livraison=commande.heure_livraison,
        adresse_livraison=commande.adresse_livraison,
        distance_km=commande.distance_km,
        frais_livraison=commande.frais_livraison,
        remise_appliquee=commande.remise_appliquee,
        prix_total=commande.prix_total,
        statut=commande.statut,
        statut_paiement=commande.statut_paiement,
        statut_materiel=commande.statut_materiel,
        date_commande=commande.date_commande,
        motif_annulation=commande.motif_annulation,
        mode_contact_annulation=commande.mode_contact_annulation,
        contact_client_effectue=commande.contact_client_effectue,
        created_at=commande.created_at,
        details=details_dto
    )