import sys
import os
from datetime import time
import bcrypt

# Rendre les modules sous app importables
sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)))

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.entities import (
    Utilisateur, UserRole,
    Regime, Allergene, Theme,
    Plat, DishType,
    Menu,
    Horaire
)


def hash_password(password: str) -> str:
    """Hache un mot de passe en utilisant bcrypt natif (rounds=12)."""
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def seed_database():
    session = SessionLocal()
    try:
        print("🌱 Début de l'injection des fixtures complètes et harmonisées...")

        # -------------------------------------------------------------------
        # 1. RÉGIMES ALIMENTAIRES
        # -------------------------------------------------------------------
        regimes_data = [
            "Végétarien",
            "Végétalien (Vegan)",
            "Sans gluten",
            "Sans lactose",
            "Halal",
            "Casher"
        ]
        regimes_map = {}
        for libelle in regimes_data:
            stmt = select(Regime).where(Regime.libelle == libelle)
            regime = session.execute(stmt).scalar_one_or_none()
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
            "Soja", "Lait", "Fruits à coque", "Moutarde", "Graines de sésame"
        ]
        allergenes_map = {}
        for libelle in allergenes_data:
            stmt = select(Allergene).where(Allergene.libelle == libelle)
            allergene = session.execute(stmt).scalar_one_or_none()
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
            "Anniversaire"
        ]
        themes_map = {}
        for libelle in themes_data:
            stmt = select(Theme).where(Theme.libelle == libelle)
            theme = session.execute(stmt).scalar_one_or_none()
            if not theme:
                theme = Theme(libelle=libelle)
                session.add(theme)
                session.flush()
            themes_map[libelle] = theme
        print("  ✓ Thèmes injectés.")

        # -------------------------------------------------------------------
        # 4. UTILISATEURS (Comptes alignés sur @vite-gourmand.fr et fixtures.sql)
        # Mot de passe unique pour tous les comptes : Password123!
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

        for u in users_data:
            stmt = select(Utilisateur).where(Utilisateur.email == u["email"])
            user = session.execute(stmt).scalar_one_or_none()
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
            else:
                user.password_hash = hash_password(u["password"])
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
            stmt = select(Horaire).where(Horaire.jour == jour)
            horaire = session.execute(stmt).scalar_one_or_none()
            if not horaire:
                session.add(Horaire(jour=jour, heure_ouverture=h_ouv, heure_fermeture=h_ferm))
        print("  ✓ Horaires injectés.")

        # -------------------------------------------------------------------
        # 6. PLATS ET ASSOCIATIONS (Allergènes, Régimes, Thèmes)
        # -------------------------------------------------------------------
        plats_definitions = [
            {
                "titre": "Carpaccio de Saint-Jacques au citron vert",
                "type_de_plat": DishType.ENTREE,
                "images_url": "/assets/images/plats/carpaccio-st-jacques.webp",
                "allergenes": ["Crustacés"],
                "regimes": [],
                "themes": ["Mariage & Réception", "Gala Événementiel"]
            },
            {
                "titre": "Velouté de potimarron et éclats de châtaigne",
                "type_de_plat": DishType.ENTREE,
                "images_url": "/assets/images/plats/veloute-potimarron.webp",
                "allergenes": ["Lait"],
                "regimes": ["Végétarien", "Sans gluten"],
                "themes": ["Cocktail Entreprise", "Buffet Champêtre"]
            },
            {
                "titre": "Salade croquante de quinoa aux agrumes",
                "type_de_plat": DishType.ENTREE,
                "images_url": "/assets/images/plats/salade-quinoa.webp",
                "allergenes": [],
                "regimes": ["Végétarien", "Végétalien (Vegan)", "Sans gluten", "Sans lactose"],
                "themes": ["Cocktail Entreprise", "Buffet Champêtre"]
            },
            {
                "titre": "Filet de bœuf rôti sauce morilles",
                "type_de_plat": DishType.MAIN_DISH,
                "images_url": "/assets/images/plats/filet-boeuf-morilles.webp",
                "allergenes": ["Lait"],
                "regimes": [],
                "themes": ["Mariage & Réception", "Gala Événementiel"]
            },
            {
                "titre": "Pavé de saumon sauvage rôti et herbes fraîches",
                "type_de_plat": DishType.MAIN_DISH,
                "images_url": "/assets/images/plats/pave-saumon.webp",
                "allergenes": ["Poissons"],
                "regimes": [],
                "themes": ["Cocktail Entreprise", "Buffet Champêtre"]
            },
            {
                "titre": "Mijoté de lentilles corail au curry doux et coco",
                "type_de_plat": DishType.MAIN_DISH,
                "images_url": "/assets/images/plats/curry-lentilles.webp",
                "allergenes": [],
                "regimes": ["Végétarien", "Végétalien (Vegan)", "Sans gluten", "Sans lactose"],
                "themes": ["Cocktail Entreprise", "Buffet Champêtre"]
            },
            {
                "titre": "Écrasé de pommes de terre à la truffe d'été",
                "type_de_plat": DishType.ACCOMPAGNEMENT,
                "images_url": "/assets/images/plats/ecrase-truffe.webp",
                "allergenes": [],
                "regimes": ["Végétarien"],
                "themes": ["Mariage & Réception", "Gala Événementiel"]
            },
            {
                "titre": "Poêlée printanière d'asperges et fèves",
                "type_de_plat": DishType.ACCOMPAGNEMENT,
                "images_url": "/assets/images/plats/poelee-legumes.webp",
                "allergenes": [],
                "regimes": ["Végétarien", "Végétalien (Vegan)", "Sans gluten", "Sans lactose"],
                "themes": ["Cocktail Entreprise", "Gala Événementiel"]
            },
            {
                "titre": "Fondant pur cacao et coulis de framboises",
                "type_de_plat": DishType.DESSERT,
                "images_url": "/assets/images/plats/fondant-chocolat.webp",
                "allergenes": ["Gluten", "Œufs", "Lait"],
                "regimes": ["Végétarien"],
                "themes": ["Mariage & Réception", "Anniversaire"]
            },
            {
                "titre": "Tartelette sablée au citron meringuée",
                "type_de_plat": DishType.DESSERT,
                "images_url": "/assets/images/plats/tartelette-citron.webp",
                "allergenes": ["Gluten", "Œufs", "Lait"],
                "regimes": ["Végétarien"],
                "themes": ["Cocktail Entreprise", "Anniversaire"]
            },
            {
                "titre": "Salade de fruits de saison parfumée à la menthe",
                "type_de_plat": DishType.DESSERT,
                "images_url": "/assets/images/plats/salade-fruits.webp",
                "allergenes": [],
                "regimes": ["Végétarien", "Végétalien (Vegan)", "Sans gluten", "Sans lactose"],
                "themes": ["Buffet Champêtre", "Anniversaire"]
            },
        ]

        plats_map = {}
        for p_def in plats_definitions:
            stmt = select(Plat).where(Plat.titre == p_def["titre"])
            plat = session.execute(stmt).scalar_one_or_none()
            if not plat:
                plat = Plat(
                    titre=p_def["titre"],
                    type_de_plat=p_def["type_de_plat"],
                    images_url=p_def["images_url"]
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
                    "Fondant pur cacao et coulis de framboises"
                ],
                "themes": ["Mariage & Réception", "Gala Événementiel"]
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
                    "Tartelette sablée au citron meringuée"
                ],
                "themes": ["Cocktail Entreprise", "Gala Événementiel"]
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
                    "Salade de fruits de saison parfumée à la menthe"
                ],
                "themes": ["Buffet Champêtre", "Anniversaire"]
            }
        ]

        for m_def in menus_definitions:
            stmt = select(Menu).where(Menu.titre == m_def["titre"])
            menu = session.execute(stmt).scalar_one_or_none()
            if not menu:
                menu = Menu(
                    titre=m_def["titre"],
                    nombre_personnes_min=m_def["nombre_personnes_min"],
                    prix_par_personne=m_def["prix_par_personne"],
                    description=m_def["description"],
                    quantite_disponible=m_def["quantite_disponible"],
                    images_url=m_def["images_url"],
                    is_active=True
                )
                for plat_titre in m_def["plats"]:
                    if plat_titre in plats_map:
                        menu.plats.append(plats_map[plat_titre])
                for theme_titre in m_def["themes"]:
                    if theme_titre in themes_map:
                        menu.themes.append(themes_map[theme_titre])
                session.add(menu)
        print("  ✓ Menus complets injectés.")

        # Valider toutes les transactions
        session.commit()
        print("\n🎉 Toutes les fixtures ont été insérées et synchronisées avec succès !")

    except Exception as e:
        session.rollback()
        print(f"\n❌ Erreur pendant l'injection des fixtures : {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()