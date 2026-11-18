import sys
import os
import json
import asyncio
from pathlib import Path
from datetime import date, time, datetime, timezone, timedelta
import bcrypt
from bson import ObjectId
import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy import select, text

# Rendre les modules sous app importables
sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)))

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.entities import (
    Utilisateur, UserRole,
    Regime, Allergene, Theme,
    Plat, DishType,
    Menu,
    Horaire,
    Commande, OrderStatus, PaymentStatus, Equipment, ContactMode,
    CommandeDetail,
    Avis, ReviewStatus, Rating,
)


def hash_password(password: str) -> str:
    """Hache un mot de passe en utilisant bcrypt natif (rounds=12)."""
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def parse_mongo_doc(doc: dict) -> dict:
    """Convertit les _id hexadécimaux en ObjectId et les dates ISO en datetime UTC."""
    parsed = {}
    for key, val in doc.items():
        if key == "_id" and isinstance(val, str) and ObjectId.is_valid(val):
            parsed[key] = ObjectId(val)
        elif key in ("created_at", "updated_at", "date_commande") and isinstance(val, str):
            parsed[key] = datetime.fromisoformat(val.replace("Z", "+00:00"))
        else:
            parsed[key] = val
    return parsed


async def seed_mongodb():
    """Réinitialise et peuple les collections MongoDB depuis database/mongo_fixtures.json."""
    fixtures_path = Path(__file__).resolve().parent / "database" / "mongo_fixtures.json"
    if not fixtures_path.exists():
        print(f"  ⚠️ Fichier introuvable : {fixtures_path}, étape MongoDB ignorée.")
        return

    with open(fixtures_path, "r", encoding="utf-8") as f:
        mongo_data = json.load(f)

    tls_kwargs = {"tls": True, "tlsCAFile": certifi.where()} if settings.MONGO_URI.startswith("mongodb+srv://") or "tls=true" in settings.MONGO_URI.lower() else {}
    client = AsyncIOMotorClient(
        settings.MONGO_URI,
        serverSelectionTimeoutMS=5000,
        **tls_kwargs,
    )
    db = client[settings.MONGO_DB]

    try:
        for collection_name in ("contacts", "avis", "commandes_stats"):
            docs = mongo_data.get(collection_name, [])
            await db[collection_name].delete_many({})
            if docs:
                prepared_docs = [parse_mongo_doc(d) for d in docs]
                await db[collection_name].insert_many(prepared_docs)
            print(f"  ✓ MongoDB '{collection_name}' réinitialisée ({len(docs)} documents).")
    finally:
        client.close()


def seed_database():
    session = SessionLocal()
    try:
        print("🌱 Début de l'injection des fixtures complètes et harmonisées (SQL + NoSQL)...")

        # -------------------------------------------------------------------
        # 1. RÉGIMES ALIMENTAIRES
        # -------------------------------------------------------------------
        regimes_data = [
            "Végétarien",
            "Végétalien (Vegan)",
            "Sans gluten",
            "Sans lactose",
            "Halal",
            "Casher",
        ]
        regimes_map = {}
        for libelle in regimes_data:
            regime = session.execute(select(Regime).where(Regime.libelle == libelle)).scalar_one_or_none()
            if not regime:
                regime = Regime(libelle=libelle)
                session.add(regime)
                session.flush()
            regimes_map[libelle] = regime
        print("  ✓ Régimes injectés.")

        # -------------------------------------------------------------------
        # 2. ALLERGÈNES
        # -------------------------------------------------------------------
        allergenes_data = [
            "Gluten", "Crustacés", "Œufs", "Poissons", "Arachides",
            "Soja", "Lait", "Fruits à coque", "Moutarde", "Graines de sésame",
        ]
        allergenes_map = {}
        for libelle in allergenes_data:
            allergene = session.execute(select(Allergene).where(Allergene.libelle == libelle)).scalar_one_or_none()
            if not allergene:
                allergene = Allergene(libelle=libelle)
                session.add(allergene)
                session.flush()
            allergenes_map[libelle] = allergene
        print("  ✓ Allergènes injectés.")

        # -------------------------------------------------------------------
        # 3. THÈMES
        # -------------------------------------------------------------------
        themes_data = [
            "Mariage & Réception",
            "Cocktail Entreprise",
            "Buffet Champêtre",
            "Gala Événementiel",
            "Anniversaire",
        ]
        themes_map = {}
        for libelle in themes_data:
            theme = session.execute(select(Theme).where(Theme.libelle == libelle)).scalar_one_or_none()
            if not theme:
                theme = Theme(libelle=libelle)
                session.add(theme)
                session.flush()
            themes_map[libelle] = theme
        print("  ✓ Thèmes injectés.")

        # -------------------------------------------------------------------
        # 4. UTILISATEURS (Alignés sur fixtures.sql)
        # -------------------------------------------------------------------
        default_pwd = "Password123!"
        users_data = [
            {
                "email": "admin@vite-gourmand.fr",
                "password": default_pwd,
                "prenom": "Sophie",
                "nom": "Directrice",
                "telephone": "0601020304",
                "adresse": "14 Rue de la Paix",
                "code_postal": "75002",
                "ville": "Paris",
                "pays": "France",
                "role": UserRole.ADMIN,
            },
            {
                "email": "employe@vite-gourmand.fr",
                "password": default_pwd,
                "prenom": "José",
                "nom": "Collaborateur",
                "telephone": "0611223344",
                "adresse": "22 Avenue Foch",
                "code_postal": "75016",
                "ville": "Paris",
                "pays": "France",
                "role": UserRole.EMPLOYE,
            },
            {
                "email": "client.durand@example.com",
                "password": default_pwd,
                "prenom": "Marc",
                "nom": "Durand",
                "telephone": "0655443322",
                "adresse": "5 Boulevard Victor Hugo",
                "code_postal": "92200",
                "ville": "Neuilly-sur-Seine",
                "pays": "France",
                "role": UserRole.CLIENT,
            },
            {
                "email": "client.leroy@example.com",
                "password": default_pwd,
                "prenom": "Claire",
                "nom": "Leroy",
                "telephone": "0677889900",
                "adresse": "18 Rue des Lilas",
                "code_postal": "94300",
                "ville": "Vincennes",
                "pays": "France",
                "role": UserRole.CLIENT,
            },
        ]

        users_map = {}
        for u in users_data:
            user = session.execute(select(Utilisateur).where(Utilisateur.email == u["email"])).scalar_one_or_none()
            if not user:
                user = Utilisateur(
                    email=u["email"],
                    password_hash=hash_password(u["password"]),
                    prenom=u["prenom"],
                    nom=u["nom"],
                    telephone=u["telephone"],
                    adresse=u["adresse"],
                    code_postal=u["code_postal"],
                    ville=u["ville"],
                    pays=u["pays"],
                    role=u["role"],
                )
                session.add(user)
                session.flush()
            else:
                user.password_hash = hash_password(u["password"])
            users_map[u["email"]] = user
        print("  ✓ Utilisateurs injectés et synchronisés.")

        # -------------------------------------------------------------------
        # 5. HORAIRES D'OUVERTURE
        # -------------------------------------------------------------------
        horaires_data = [
            ("Lundi", time(8, 0), time(19, 0)),
            ("Mardi", time(8, 0), time(19, 0)),
            ("Mercredi", time(8, 0), time(19, 0)),
            ("Jeudi", time(8, 0), time(20, 0)),
            ("Vendredi", time(8, 0), time(22, 0)),
            ("Samedi", time(7, 30), time(23, 0)),
            ("Dimanche", time(8, 0), time(16, 0)),
        ]
        for jour, h_ouv, h_ferm in horaires_data:
            horaire = session.execute(select(Horaire).where(Horaire.jour == jour)).scalar_one_or_none()
            if not horaire:
                session.add(Horaire(jour=jour, heure_ouverture=h_ouv, heure_fermeture=h_ferm))
        print("  ✓ Horaires injectés.")

        # -------------------------------------------------------------------
        # 6. PLATS ET ASSOCIATIONS
        # -------------------------------------------------------------------
        plats_definitions = [
            {
                "titre": "Carpaccio de Saint-Jacques au citron vert",
                "type_de_plat": DishType.ENTREE,
                "images_url": "/assets/images/plats/carpaccio-st-jacques.webp",
                "allergenes": ["Crustacés"],
                "regimes": [],
                "themes": ["Mariage & Réception", "Gala Événementiel"],
            },
            {
                "titre": "Velouté de potimarron et éclats de châtaigne",
                "type_de_plat": DishType.ENTREE,
                "images_url": "/assets/images/plats/veloute-potimarron.webp",
                "allergenes": ["Lait"],
                "regimes": ["Végétarien", "Sans gluten"],
                "themes": ["Cocktail Entreprise", "Buffet Champêtre"],
            },
            {
                "titre": "Salade croquante de quinoa aux agrumes",
                "type_de_plat": DishType.ENTREE,
                "images_url": "/assets/images/plats/salade-quinoa.webp",
                "allergenes": [],
                "regimes": ["Végétarien", "Végétalien (Vegan)", "Sans gluten", "Sans lactose"],
                "themes": ["Cocktail Entreprise", "Buffet Champêtre"],
            },
            {
                "titre": "Filet de bœuf rôti sauce morilles",
                "type_de_plat": DishType.MAIN_DISH,
                "images_url": "/assets/images/plats/filet-boeuf-morilles.webp",
                "allergenes": ["Lait"],
                "regimes": [],
                "themes": ["Mariage & Réception", "Gala Événementiel"],
            },
            {
                "titre": "Pavé de saumon sauvage rôti et herbes fraîches",
                "type_de_plat": DishType.MAIN_DISH,
                "images_url": "/assets/images/plats/pave-saumon.webp",
                "allergenes": ["Poissons"],
                "regimes": [],
                "themes": ["Cocktail Entreprise", "Buffet Champêtre"],
            },
            {
                "titre": "Mijoté de lentilles corail au curry doux et coco",
                "type_de_plat": DishType.MAIN_DISH,
                "images_url": "/assets/images/plats/curry-lentilles.webp",
                "allergenes": [],
                "regimes": ["Végétarien", "Végétalien (Vegan)", "Sans gluten", "Sans lactose"],
                "themes": ["Cocktail Entreprise", "Buffet Champêtre"],
            },
            {
                "titre": "Écrasé de pommes de terre à la truffe d'été",
                "type_de_plat": DishType.ACCOMPAGNEMENT,
                "images_url": "/assets/images/plats/ecrase-truffe.webp",
                "allergenes": [],
                "regimes": ["Végétarien"],
                "themes": ["Mariage & Réception", "Gala Événementiel"],
            },
            {
                "titre": "Poêlée printanière d'asperges et fèves",
                "type_de_plat": DishType.ACCOMPAGNEMENT,
                "images_url": "/assets/images/plats/poelee-legumes.webp",
                "allergenes": [],
                "regimes": ["Végétarien", "Végétalien (Vegan)", "Sans gluten", "Sans lactose"],
                "themes": ["Cocktail Entreprise", "Gala Événementiel"],
            },
            {
                "titre": "Fondant pur cacao et coulis de framboises",
                "type_de_plat": DishType.DESSERT,
                "images_url": "/assets/images/plats/fondant-chocolat.webp",
                "allergenes": ["Gluten", "Œufs", "Lait"],
                "regimes": ["Végétarien"],
                "themes": ["Mariage & Réception", "Anniversaire"],
            },
            {
                "titre": "Tartelette sablée au citron meringuée",
                "type_de_plat": DishType.DESSERT,
                "images_url": "/assets/images/plats/tartelette-citron.webp",
                "allergenes": ["Gluten", "Œufs", "Lait"],
                "regimes": ["Végétarien"],
                "themes": ["Cocktail Entreprise", "Anniversaire"],
            },
            {
                "titre": "Salade de fruits de saison parfumée à la menthe",
                "type_de_plat": DishType.DESSERT,
                "images_url": "/assets/images/plats/salade-fruits.webp",
                "allergenes": [],
                "regimes": ["Végétarien", "Végétalien (Vegan)", "Sans gluten", "Sans lactose"],
                "themes": ["Buffet Champêtre", "Anniversaire"],
            },
        ]

        plats_map = {}
        for p_def in plats_definitions:
            plat = session.execute(select(Plat).where(Plat.titre == p_def["titre"])).scalar_one_or_none()
            if not plat:
                plat = Plat(
                    titre=p_def["titre"],
                    type_de_plat=p_def["type_de_plat"],
                    images_url=p_def["images_url"],
                )
                for alg_name in p_def.get("allergenes", []):
                    if alg_name in allergenes_map:
                        plat.allergenes.append(allergenes_map[alg_name])
                for reg_name in p_def.get("regimes", []):
                    if reg_name in regimes_map:
                        plat.regimes.append(regimes_map[reg_name])
                for th_name in p_def.get("themes", []):
                    if th_name in themes_map:
                        plat.themes.append(themes_map[th_name])
                session.add(plat)
                session.flush()
            plats_map[p_def["titre"]] = plat
        print("  ✓ Plats de démonstration injectés.")

        # -------------------------------------------------------------------
        # 7. MENUS COMPLETS
        # -------------------------------------------------------------------
        menus_definitions = [
            {
                "titre": "Menu Prestige des Grands Jours",
                "nombre_personnes_min": 10,
                "prix_par_personne": 48.00,
                "description": "Une sélection raffinée associant Saint-Jacques et bœuf truffé pour des événements d'exception.",
                "quantite_disponible": 150,
                "images_url": "/assets/images/menus/prestige.webp",
                "plats": [
                    "Carpaccio de Saint-Jacques au citron vert",
                    "Filet de bœuf rôti sauce morilles",
                    "Écrasé de pommes de terre à la truffe d'été",
                    "Fondant pur cacao et coulis de framboises",
                ],
                "themes": ["Mariage & Réception", "Gala Événementiel"],
            },
            {
                "titre": "Menu Cocktail Signature",
                "nombre_personnes_min": 15,
                "prix_par_personne": 32.50,
                "description": "Formule dînatoire complète idéale pour les soirées professionnelles et réceptions d'entreprise.",
                "quantite_disponible": 300,
                "images_url": "/assets/images/menus/cocktail.webp",
                "plats": [
                    "Velouté de potimarron et éclats de châtaigne",
                    "Pavé de saumon sauvage rôti et herbes fraîches",
                    "Poêlée printanière d'asperges et fèves",
                    "Tartelette sablée au citron meringuée",
                ],
                "themes": ["Cocktail Entreprise", "Gala Événementiel"],
            },
            {
                "titre": "Menu Champêtre & Végétal",
                "nombre_personnes_min": 8,
                "prix_par_personne": 26.00,
                "description": "Élaboré intégralement à partir de produits frais de saison, labellisé végétarien et sans gluten.",
                "quantite_disponible": 100,
                "images_url": "/assets/images/menus/vegetal.webp",
                "plats": [
                    "Velouté de potimarron et éclats de châtaigne",
                    "Salade croquante de quinoa aux agrumes",
                    "Mijoté de lentilles corail au curry doux et coco",
                    "Salade de fruits de saison parfumée à la menthe",
                ],
                "themes": ["Buffet Champêtre", "Anniversaire"],
            },
        ]

        menus_map = {}
        for m_def in menus_definitions:
            menu = session.execute(select(Menu).where(Menu.titre == m_def["titre"])).scalar_one_or_none()
            if not menu:
                menu = Menu(
                    titre=m_def["titre"],
                    nombre_personnes_min=m_def["nombre_personnes_min"],
                    prix_par_personne=m_def["prix_par_personne"],
                    description=m_def["description"],
                    quantite_disponible=m_def["quantite_disponible"],
                    images_url=m_def["images_url"],
                    is_active=True,
                )
                for plat_titre in m_def["plats"]:
                    if plat_titre in plats_map:
                        menu.plats.append(plats_map[plat_titre])
                for theme_titre in m_def["themes"]:
                    if theme_titre in themes_map:
                        menu.themes.append(themes_map[theme_titre])
                session.add(menu)
                session.flush()
            menus_map[m_def["titre"]] = menu
        print("  ✓ Menus complets injectés.")

        # -------------------------------------------------------------------
        # 8. COMMANDES DE DÉMONSTRATION + LIGNES DE COMMANDE (Alignées fixtures.sql)
        # -------------------------------------------------------------------
        tz_plus_2 = timezone(timedelta(hours=2))
        tz_plus_1 = timezone(timedelta(hours=1))

        commandes_definitions = [
            {
                "numero_commande": "CMD-2026-0001",
                "client_email": "client.durand@example.com",
                "date_prestation": date(2026, 10, 15),
                "heure_livraison": time(12, 30),
                "prix_total": 960.00,
                "remise_appliquee": 0.0,
                "adresse_livraison": "5 Boulevard Victor Hugo, 92200 Neuilly-sur-Seine",
                "distance_km": 8.5,
                "frais_livraison": 12.50,
                "statut": OrderStatus.COMPLETED,
                "date_commande": datetime(2026, 10, 1, 9, 15, tzinfo=tz_plus_2),
                "statut_paiement": PaymentStatus.PAID,
                "statut_materiel": Equipment.RETURNED,
                "contact_client_effectue": False,
                "motif_annulation": None,
                "mode_contact_annulation": None,
                "details": [
                    {
                        "menu_titre": "Menu Prestige des Grands Jours",
                        "quantite": 20,
                        "prix_applique": 48.00,
                    }
                ],
            },
            {
                "numero_commande": "CMD-2026-0002",
                "client_email": "client.leroy@example.com",
                "date_prestation": date(2026, 11, 20),
                "heure_livraison": time(19, 30),
                "prix_total": 1170.00,
                "remise_appliquee": 130.00,
                "adresse_livraison": "18 Rue des Lilas, 94300 Vincennes",
                "distance_km": 14.0,
                "frais_livraison": 18.00,
                "statut": OrderStatus.CONFIRMED,
                "date_commande": datetime(2026, 11, 2, 14, 20, tzinfo=tz_plus_1),
                "statut_paiement": PaymentStatus.DUE,
                "statut_materiel": Equipment.INCLUDED,
                "contact_client_effectue": False,
                "motif_annulation": None,
                "mode_contact_annulation": None,
                "details": [
                    {
                        "menu_titre": "Menu Cocktail Signature",
                        "quantite": 40,
                        "prix_applique": 32.50,
                    }
                ],
            },
            {
                "numero_commande": "CMD-2026-0003",
                "client_email": "client.durand@example.com",
                "date_prestation": date(2026, 11, 5),
                "heure_livraison": time(11, 30),
                "prix_total": 260.00,
                "remise_appliquee": 0.0,
                "adresse_livraison": "5 Boulevard Victor Hugo, 92200 Neuilly-sur-Seine",
                "distance_km": 8.5,
                "frais_livraison": 12.50,
                "statut": OrderStatus.CANCELLED,
                "date_commande": datetime(2026, 10, 28, 16, 45, tzinfo=tz_plus_1),
                "statut_paiement": PaymentStatus.CANCELLED,
                "statut_materiel": Equipment.NON_INCLUDED,
                "contact_client_effectue": True,
                "motif_annulation": "Impossibilité technique suite à panne de chambre froide.",
                "mode_contact_annulation": ContactMode.TELEPHONE,
                "details": [
                    {
                        "menu_titre": "Menu Champêtre & Végétal",
                        "quantite": 10,
                        "prix_applique": 26.00,
                    }
                ],
            },
        ]

        for cmd_def in commandes_definitions:
            cmd = session.execute(
                select(Commande).where(Commande.numero_commande == cmd_def["numero_commande"])
            ).scalar_one_or_none()
            if not cmd:
                client_user = users_map[cmd_def["client_email"]]
                cmd = Commande(
                    numero_commande=cmd_def["numero_commande"],
                    user_id=client_user.user_id,
                    date_prestation=cmd_def["date_prestation"],
                    heure_livraison=cmd_def["heure_livraison"],
                    prix_total=cmd_def["prix_total"],
                    remise_appliquee=cmd_def["remise_appliquee"],
                    adresse_livraison=cmd_def["adresse_livraison"],
                    distance_km=cmd_def["distance_km"],
                    frais_livraison=cmd_def["frais_livraison"],
                    statut=cmd_def["statut"],
                    date_commande=cmd_def["date_commande"],
                    statut_paiement=cmd_def["statut_paiement"],
                    statut_materiel=cmd_def["statut_materiel"],
                    contact_client_effectue=cmd_def["contact_client_effectue"],
                    motif_annulation=cmd_def["motif_annulation"],
                    mode_contact_annulation=cmd_def["mode_contact_annulation"],
                )
                for det in cmd_def["details"]:
                    menu_obj = menus_map[det["menu_titre"]]
                    cmd.details.append(
                        CommandeDetail(
                            menu_id=menu_obj.menu_id,
                            quantite=det["quantite"],
                            prix_applique=det["prix_applique"],
                        )
                    )
                session.add(cmd)
        print("  ✓ Commandes de démonstration et lignes de détails injectées.")

        # -------------------------------------------------------------------
        # 9. AVIS CLIENTS (Aligné sur fixtures.sql)
        # -------------------------------------------------------------------
        avis_desc = "Prestation irréprochable. Le bœuf aux morilles a fait l'unanimité auprès de nos convives."
        existing_avis = session.execute(select(Avis).where(Avis.description == avis_desc)).scalar_one_or_none()
        if not existing_avis:
            session.add(
                Avis(
                    description=avis_desc,
                    user_id=users_map["client.durand@example.com"].user_id,
                    menu_id=menus_map["Menu Prestige des Grands Jours"].menu_id,
                    statut=ReviewStatus.APPROVED,
                    qualite=Rating.EXCELLENT,
                    service=Rating.EXCELLENT,
                    prix=Rating.GOOD,
                )
            )
        print("  ✓ Avis client PostgreSQL injecté.")

        # Valider toutes les transactions SQL
        session.commit()

        # Réalignement des séquences PostgreSQL
        sequences = [
            ("public.utilisateurs_user_id_seq", "public.utilisateurs", "user_id"),
            ("public.menus_menu_id_seq", "public.menus", "menu_id"),
            ("public.plats_plat_id_seq", "public.plats", "plat_id"),
            ("public.allergenes_allergene_id_seq", "public.allergenes", "allergene_id"),
            ("public.regimes_regime_id_seq", "public.regimes", "regime_id"),
            ("public.themes_theme_id_seq", "public.themes", "theme_id"),
            ("public.horaires_horaire_id_seq", "public.horaires", "horaire_id"),
            ("public.commandes_commande_id_seq", "public.commandes", "commande_id"),
            ("public.commande_details_detail_id_seq", "public.commande_details", "detail_id"),
            ("public.avis_avis_id_seq", "public.avis", "avis_id"),
        ]
        for seq_name, table_name, pk_col in sequences:
            session.execute(
                text(f"SELECT setval('{seq_name}', COALESCE((SELECT MAX({pk_col}) FROM {table_name}), 1))")
            )
        session.commit()
        print("  ✓ Séquences PostgreSQL réalignées.")

        # -------------------------------------------------------------------
        # 10. RÉINITIALISATION & PEUPLEMENT MONGODB ATLAS
        # -------------------------------------------------------------------
        asyncio.run(seed_mongodb())

        print("\n🎉 Toutes les fixtures SQL et NoSQL ont été insérées et synchronisées avec succès !")

    except Exception as e:
        session.rollback()
        print(f"\n❌ Erreur pendant l'injection des fixtures : {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()