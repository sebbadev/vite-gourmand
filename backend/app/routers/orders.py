from datetime import date, time, datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db, get_mongo_db
from app.core.deps import get_current_user, require_client, require_employe
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
    OrderItemCreate,
    QuoteRequest,
    QuoteResponse,
    OrderCreate,
    OrderUpdate,
    OrderRead,
    OrderDetailRead,
    OrderStatusUpdate, 
    OrderCancelRequest,
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



# Matrice des transitions logistiques séquentielles autorisées
ALLOWED_TRANSITIONS = {
    OrderStatus.PENDING: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
    OrderStatus.CONFIRMED: [OrderStatus.PREPARING, OrderStatus.CANCELLED],
    OrderStatus.PREPARING: [OrderStatus.READY, OrderStatus.CANCELLED],
    OrderStatus.READY: [OrderStatus.DELIVERED],
    OrderStatus.DELIVERED: [OrderStatus.COMPLETED],
    OrderStatus.COMPLETED: [],
    OrderStatus.CANCELLED: [],
}


@router.patch(
    "/{commande_id}/statut",
    response_model=OrderRead,
    summary="Mise à jour du statut logistique, paiement et matériel (Employé & Admin)"
)
async def update_order_status(
    commande_id: int,
    status_update: OrderStatusUpdate,
    current_user: Utilisateur = Depends(require_employe),
    db: Session = Depends(get_db),
    mongo = Depends(get_mongo_db)
):
    """
    Fait progresser le statut d'une commande selon le workflow logistique.
    Vérifie les prérequis de clôture pour le statut 'Terminée' :
    - La commande doit être déjà Livrée
    - Le paiement doit être Réglé
    - Le matériel doit être Retourné ou Non inclus
    Synchronise automatiquement vers la collection MongoDB 'commandes_stats' à la finalisation.
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

    # 1. Mise à jour préalable des statuts annexes (paiement et matériel)
    if status_update.statut_paiement:
        commande.statut_paiement = status_update.statut_paiement

    if status_update.statut_materiel:
        commande.statut_materiel = status_update.statut_materiel

    # 2. Transition de statut logistique
    if status_update.nouveau_statut and status_update.nouveau_statut != commande.statut:
        nouveau = status_update.nouveau_statut
        autorises = ALLOWED_TRANSITIONS.get(commande.statut, [])

        if nouveau not in autorises:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Transition non autorisée de '{commande.statut.value}' vers '{nouveau.value}'. "
                    f"Statuts possibles : {[s.value for s in autorises]}."
                )
            )

        # Règle stricte de clôture : 'Terminée' exige paiement soldé et matériel restitué
        if nouveau == OrderStatus.COMPLETED:
            if commande.statut_paiement != PaymentStatus.PAID:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Impossible de clôturer la commande : le règlement doit être 'Réglée'."
                )
            if commande.statut_materiel == Equipment.INCLUDED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Impossible de clôturer la commande : le matériel prêté doit être 'Retourné' ou 'Non inclus'."
                )

        commande.statut = nouveau

    db.commit()
    db.refresh(commande)

    # 3. Synchronisation analytique vers MongoDB si la commande est 'Terminée'
    if commande.statut == OrderStatus.COMPLETED:
        try:
            # Calcul du split HT / TVA 10%
            montant_ttc = commande.prix_total
            montant_ht = round(montant_ttc / 1.10, 2)
            montant_tva = round(montant_ttc - montant_ht, 2)

            # Date et calendrier
            d_prest = commande.date_prestation
            cal = d_prest.isocalendar()

            menus_stats = [
                {
                    "menu_id": d.menu_id,
                    "titre": d.menu.titre if d.menu else "Menu",
                    "quantite": d.quantite,
                    "prix_unitaire": d.prix_applique,
                    "total_ligne": round(d.quantite * d.prix_applique, 2)
                }
                for d in commande.details
            ]

            doc_stats = {
                "commande_id": commande.commande_id,
                "numero_commande": commande.numero_commande,
                "date_commande": commande.date_commande,
                "date_prestation": str(commande.date_prestation),
                "annee": d_prest.year,
                "mois": d_prest.month,
                "semaine": cal[1],
                "montant_ht": montant_ht,
                "montant_tva": montant_tva,
                "montant_ttc": montant_ttc,
                "remise_appliquee": commande.remise_appliquee,
                "frais_livraison": commande.frais_livraison,
                "distance_km": commande.distance_km,
                "menus": menus_stats
            }

            # Upsert dans MongoDB pour éviter les doublons
            await mongo.commandes_stats.update_one(
                {"commande_id": commande.commande_id},
                {"$set": doc_stats},
                upsert=True
            )
        except Exception:
            # En environnement transactionnel, un échec NoSQL n'invalide pas la transaction SQL
            pass

    # Restitution DTO
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


@router.patch(
    "/{commande_id}",
    response_model=OrderRead,
    summary="Modification d'une commande en attente par le client (hors changement de menu)"
)
def update_pending_order(
    commande_id: int,
    date_prestation: Optional[date] = Query(None, description="Nouvelle date de prestation (AAAA-MM-JJ)"),
    heure_livraison: Optional[time] = Query(None, description="Nouvelle heure de livraison (HH:MM:SS)"),
    adresse_livraison: Optional[str] = Query(None, min_length=5, max_length=255, description="Nouvelle adresse de livraison"),
    distance_km: Optional[float] = Query(None, ge=0.0, description="Nouvelle distance kilométrique"),
    quantite: Optional[int] = Query(None, gt=0, description="Nouveau nombre de convives (pour une commande à menu unique)"),
    order_in: Optional[OrderUpdate] = None,
    current_user: Utilisateur = Depends(require_client),
    db: Session = Depends(get_db)
):
    """
    Permet au client de modifier sa commande tant qu'elle est 'En attente de validation' :
    - Via les champs individuels Swagger (Query) : date, heure, adresse, distance, et quantité (si menu unique)
    - Via le corps JSON (OrderUpdate) : modification des quantités sur une commande multi-menus
    - Recalcul automatique des tarifs (RG-01 à RG-03) et réajustement des stocks.
    """
    stmt = (
        select(Commande)
        .where(Commande.commande_id == commande_id, Commande.is_deleted.is_(False))
        .options(selectinload(Commande.details).selectinload(CommandeDetail.menu))
    )
    commande = db.execute(stmt).scalar_one_or_none()

    if not commande:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commande introuvable.")

    if commande.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé à cette commande.")

    if commande.statut != OrderStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Modification impossible : la commande a déjà été acceptée ou traitée."
        )

    # Fusion des valeurs logistiques (priorité aux paramètres Query)
    new_date = date_prestation if date_prestation is not None else (order_in.date_prestation if order_in else None)
    new_time = heure_livraison if heure_livraison is not None else (order_in.heure_livraison if order_in else None)
    new_address = adresse_livraison if adresse_livraison is not None else (order_in.adresse_livraison if order_in else None)
    new_distance = distance_km if distance_km is not None else (order_in.distance_km if order_in else None)

    if new_date is not None:
        commande.date_prestation = new_date
    if new_time is not None:
        commande.heure_livraison = new_time
    if new_address is not None:
        commande.adresse_livraison = new_address
    if new_distance is not None:
        commande.distance_km = new_distance

    # 2. Gestion des quantités (soit via le champ simple 'quantite', soit via la liste 'items' en JSON)
    if quantite is not None:
        if len(commande.details) > 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cette commande contient plusieurs menus : veuillez utiliser le corps JSON (items) pour préciser les quantités par menu."
            )
        detail = commande.details[0]
        delta = quantite - detail.quantite
        if delta > 0 and detail.menu.quantite_disponible < delta:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuffisant pour ajouter {delta} convive(s) sur '{detail.menu.titre}'."
            )
        detail.menu.quantite_disponible -= delta
        detail.quantite = quantite

    elif order_in and order_in.items is not None:
        existing_menu_ids = {d.menu_id for d in commande.details}
        new_menu_ids = {item.menu_id for item in order_in.items}

        if existing_menu_ids != new_menu_ids or len(order_in.items) != len(commande.details):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Conformément au cahier des charges, le changement de menu n'est pas autorisé. Veuillez annuler et repasser commande."
            )

        items_map = {item.menu_id: item.quantite for item in order_in.items}

        for detail in commande.details:
            nouvelle_qte = items_map[detail.menu_id]
            delta = nouvelle_qte - detail.quantite

            if delta > 0 and detail.menu.quantite_disponible < delta:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Stock insuffisant pour ajouter {delta} convive(s) sur '{detail.menu.titre}'."
                )

            detail.menu.quantite_disponible -= delta
            detail.quantite = nouvelle_qte

    # 3. Recalcul global du devis (vérifie également que la nouvelle quantité respecte toujours nombre_personnes_min)
    items_for_quote = [
        OrderItemCreate(menu_id=d.menu_id, quantite=d.quantite)
        for d in commande.details
    ]
    quote = calculate_order_quote(
        items=items_for_quote,
        distance_km=commande.distance_km,
        db=db
    )

    commande.frais_livraison = quote.frais_livraison
    commande.remise_appliquee = quote.remise_appliquee
    commande.prix_total = quote.prix_total

    db.commit()
    db.refresh(commande)

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


@router.post(
    "/{commande_id}/annuler",
    response_model=OrderRead,
    summary="Annulation d'une commande (Autonome client avant acceptation, ou employé avec contact)"
)
def cancel_order(
    commande_id: int,
    cancel_in: Optional[OrderCancelRequest] = None,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Annule une commande et restitue les stocks de menus :
    - Un client ne peut annuler QUE si la commande est 'En attente de validation'.
    - Un employé/admin doit obligatoirement justifier le motif et confirmer le contact préalable du client.
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

    if commande.statut in [OrderStatus.CANCELLED, OrderStatus.COMPLETED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Impossible d'annuler une commande déjà au statut '{commande.statut.value}'."
        )

    # 1. Règles selon le rôle
    if current_user.role == UserRole.CLIENT:
        if commande.user_id != current_user.user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé.")
        if commande.statut != OrderStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="L'annulation autonome n'est autorisée que tant que la commande est 'En attente de validation'."
            )
        commande.motif_annulation = cancel_in.motif_annulation if cancel_in else None or "Annulation par le client"
        commande.contact_client_effectue = True
    else:
        # Employé ou Admin
        if not cancel_in.motif_annulation or not cancel_in.mode_contact_annulation or not cancel_in.contact_client_effectue:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "L'annulation par le restaurant exige obligatoirement un motif, "
                    "le mode de contact (Téléphone/Email) et la confirmation de contact préalable."
                )
            )
        commande.motif_annulation = cancel_in.motif_annulation
        commande.mode_contact_annulation = cancel_in.mode_contact_annulation
        commande.contact_client_effectue = cancel_in.contact_client_effectue

    # 2. Bascule des statuts
    commande.statut = OrderStatus.CANCELLED
    commande.statut_paiement = PaymentStatus.CANCELLED

    # 3. Restitution des stocks en base
    for detail in commande.details:
        if detail.menu:
            detail.menu.quantite_disponible += detail.quantite

    db.commit()
    db.refresh(commande)

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