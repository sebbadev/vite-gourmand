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
    """Hache un mot de passe en utilisant bcrypt natif (sel généré automatiquement)."""
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def seed_database():
    session = SessionLocal()
    try:
        print("🌱 Début de l'injection des fixtures...")

        # -------------------------------------------------------------------
        # 1. RÉGIMES ALIMENTAIRES
        # -------------------------------------------------------------------
        regimes_data = [
            "Végétarien",
            "Végan",
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
            "Soja", "Lait / Lactose", "Fruits à coque", "Céleri",
            "Moutarde", "Graines de sésame", "Sulfites"
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
            "Mariage & Cérémonie",
            "Séminaire & Entreprise",
            "Anniversaire",
            "Cocktail Dînatoire",
            "Gastronomique Français",
            "Saveurs du Monde"
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
        # 4. UTILISATEURS DE TEST (1 de chaque rôle)
        # -------------------------------------------------------------------
        users_data = [
            {
                "email": "admin@vitegourmand.fr",
                "password": "AdminPassword123!",
                "prenom": "Alice",
                "nom": "Administrateur",
                "telephone": "0601020304",
                "adresse": "10 Rue Royale",
                "code_postal": "75008",
                "ville": "Paris",
                "pays": "France",
                "role": UserRole.ADMIN,
            },
            {
                "email": "chef@vitegourmand.fr",
                "password": "ChefPassword123!",
                "prenom": "Bernard",
                "nom": "Bocuse",
                "telephone": "0602030405",
                "adresse": "12 Quai de la Pêcherie",
                "code_postal": "69001",
                "ville": "Lyon",
                "pays": "France",
                "role": UserRole.EMPLOYE,
            },
            {
                "email": "employe@vitegourmand.fr",
                "password": "EmployePassword123!",
                "prenom": "Chloé",
                "nom": "Livreuse",
                "telephone": "0603040506",
                "adresse": "5 Rue des Fleurs",
                "code_postal": "33000",
                "ville": "Bordeaux",
                "pays": "France",
                "role": UserRole.EMPLOYE,
            },
            {
                "email": "client@vitegourmand.fr",
                "password": "ClientPassword123!",
                "prenom": "David",
                "nom": "Dupont",
                "telephone": "0604050607",
                "adresse": "8 Avenue Jean Jaurès",
                "code_postal": "59000",
                "ville": "Lille",
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
        print("  ✓ Utilisateurs de test injectés.")

        # -------------------------------------------------------------------
        # 5. HORAIRES D'OUVERTURE
        # -------------------------------------------------------------------
        horaires_data = [
            ("Lundi", time(9, 0), time(19, 0)),
            ("Mardi", time(9, 0), time(19, 0)),
            ("Mercredi", time(9, 0), time(19, 0)),
            ("Jeudi", time(9, 0), time(19, 0)),
            ("Vendredi", time(9, 0), time(21, 0)),
            ("Samedi", time(10, 0), time(22, 0)),
            ("Dimanche", time(10, 0), time(15, 0)),
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
                "titre": "Velouté de potimarron et châtaignes",
                "type_de_plat": DishType.ENTREE,
                "images_url": "https://images.unsplash.com/photo-1547592166-23ac45744acd",
                "allergenes": ["Lait / Lactose"],
                "regimes": ["Végétarien", "Sans gluten"],
                "themes": ["Gastronomique Français", "Automne & Hiver"]
            },
            {
                "titre": "Tartare de saumon d'Isigny et aneth",
                "type_de_plat": DishType.ENTREE,
                "images_url": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb",
                "allergenes": ["Poissons"],
                "regimes": ["Sans gluten", "Sans lactose"],
                "themes": ["Cocktail Dînatoire"]
            },
            {
                "titre": "Suprême de volaille fermière aux morilles",
                "type_de_plat": DishType.MAIN_DISH,
                "images_url": "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d",
                "allergenes": ["Lait / Lactose"],
                "regimes": ["Sans gluten", "Halal"],
                "themes": ["Mariage & Cérémonie", "Gastronomique Français"]
            },
            {
                "titre": "Risotto crémeux aux asperges vertes et parmesan",
                "type_de_plat": DishType.MAIN_DISH,
                "images_url": "https://images.unsplash.com/photo-1633964913295-ceb43826e7c9",
                "allergenes": ["Lait / Lactose"],
                "regimes": ["Végétarien", "Sans gluten"],
                "themes": ["Mariage & Cérémonie"]
            },
            {
                "titre": "Mousse légère au chocolat noir Valrhona",
                "type_de_plat": DishType.DESSERT,
                "images_url": "https://images.unsplash.com/photo-1541781774459-bb2af2f05b55",
                "allergenes": ["Œufs", "Lait / Lactose"],
                "regimes": ["Végétarien", "Sans gluten"],
                "themes": ["Anniversaire", "Gastronomique Français"]
            },
            {
                "titre": "Tartelette sablée aux framboises fraîches",
                "type_de_plat": DishType.DESSERT,
                "images_url": "https://images.unsplash.com/photo-1565958011703-44f9829ba187",
                "allergenes": ["Gluten", "Lait / Lactose", "Œufs"],
                "regimes": ["Végétarien"],
                "themes": ["Cocktail Dînatoire", "Anniversaire"]
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
                "titre": "Menu Prestige d'Antan",
                "nombre_personnes_min": 6,
                "prix_par_personne": 48.50,
                "description": "Un voyage gastronomique d'exception conçu pour vos célébrations, mariages et réceptions privées.",
                "quantite_disponible": 40,
                "images_url": "https://images.unsplash.com/photo-1555244162-803834f70033",
                "plats": [
                    "Tartare de saumon d'Isigny et aneth",
                    "Suprême de volaille fermière aux morilles",
                    "Mousse légère au chocolat noir Valrhona"
                ],
                "themes": ["Mariage & Cérémonie", "Gastronomique Français"]
            },
            {
                "titre": "Menu Terroir & Végétal",
                "nombre_personnes_min": 4,
                "prix_par_personne": 36.00,
                "description": "Une alliance délicate de produits de saison 100 % végétariens et sans compromis sur la gourmandise.",
                "quantite_disponible": 25,
                "images_url": "https://images.unsplash.com/photo-1540420773420-3366772f4999",
                "plats": [
                    "Velouté de potimarron et châtaignes",
                    "Risotto crémeux aux asperges vertes et parmesan",
                    "Tartelette sablée aux framboises fraîches"
                ],
                "themes": ["Anniversaire", "Séminaire & Entreprise"]
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
        print("\n🎉 Toutes les fixtures ont été insérées avec succès dans PostgreSQL 18 !")

    except Exception as e:
        session.rollback()
        print(f"\n❌ Erreur pendant l'injection des fixtures : {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()