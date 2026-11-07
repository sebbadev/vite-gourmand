# Diagramme de Classes — Vite & Gourmand (UML)

Ce diagramme modélise l'architecture complète des entités relationnelles, leurs énumérations métier associées, ainsi que leurs relations et cardinalités. Il est en stricte conformité avec le schéma PostgreSQL (`create_db.sql`) et les modèles SQLAlchemy du backend (`models.py`).

---

## 1. Diagramme Mermaid

```mermaid
classDiagram
    direction TB

    %% ==========================================
    %% ÉNUMÉRATIONS (Types Métier)
    %% ==========================================
    class UserRole {
        <<enumeration>>
        ADMINISTRATEUR
        EMPLOYE
        CLIENT
    }

    class DishType {
        <<enumeration>>
        ENTREE
        PLAT_PRINCIPAL
        ACCOMPAGNEMENT
        DESSERT
    }

    class OrderStatus {
        <<enumeration>>
        EN_ATTENTE_DE_VALIDATION
        ACCEPTEE
        ANNULEE
        EN_PREPARATION
        EN_COURS_DE_LIVRAISON
        LIVREE
        TERMINEE
    }

    class PaymentStatus {
        <<enumeration>>
        EN_ATTENTE_DE_REGLEMENT
        ANNULEE
        REGLEE
    }

    class Equipment {
        <<enumeration>>
        INCLUS
        NON_INCLUS
        RETOURNE
    }

    class ContactMode {
        <<enumeration>>
        TELEPHONE
        EMAIL
    }

    class ReviewStatus {
        <<enumeration>>
        EN_ATTENTE
        APPROUVE
        REPONDU
        REJETE
    }

    class Rating {
        <<enumeration>>
        CRITIQUE
        A_AMELIORER
        CORRECT
        BIEN
        EXCELLENT
    }

    %% ==========================================
    %% CLASSES DU DOMAINE
    %% ==========================================
    class Utilisateur {
        +int user_id
        +string email
        +string password_hash
        +string nom
        +string prenom
        +string telephone
        +string adresse
        +string code_postal
        +string ville
        +string pays
        +UserRole role
        +datetime created_at
        +datetime updated_at
        +bool is_deleted
    }

    class Menu {
        +int menu_id
        +string titre
        +string description
        +float prix_par_personne
        +int nombre_personnes_min
        +int quantite_disponible
        +string images_url
        +bool is_active
        +datetime created_at
        +datetime updated_at
        +bool is_deleted
    }

    class Plat {
        +int plat_id
        +string titre
        +DishType type_de_plat
        +string images_url
    }

    class Commande {
        +int commande_id
        +string numero_commande
        +int user_id
        +date date_prestation
        +datetime heure_livraison
        +float prix_total
        +float remise_appliquee
        +string adresse_livraison
        +float distance_km
        +float frais_livraison
        +OrderStatus statut
        +datetime date_commande
        +PaymentStatus statut_paiement
        +Equipment statut_materiel
        +string motif_annulation
        +ContactMode mode_contact_annulation
        +bool contact_client_effectue
        +datetime updated_at
        +bool is_deleted
    }

    class CommandeDetail {
        +int detail_id
        +int commande_id
        +int menu_id
        +int quantite
        +float prix_applique
        +datetime created_at
        +datetime updated_at
        +bool is_deleted
    }

    class Avis {
        +int avis_id
        +int user_id
        +int menu_id
        +string description
        +ReviewStatus statut
        +Rating qualite
        +Rating service
        +Rating prix
        +datetime created_at
        +datetime updated_at
        +bool is_deleted
    }

    class Horaire {
        +int horaire_id
        +string jour
        +time heure_ouverture
        +time heure_fermeture
        +datetime created_at
        +datetime updated_at
        +bool is_deleted
    }

    class Theme {
        +int theme_id
        +string libelle
    }

    class Regime {
        +int regime_id
        +string libelle
    }

    class Allergene {
        +int allergene_id
        +string libelle
    }

    %% ==========================================
    %% RELATIONS ET CARDINALITÉS
    %% ==========================================
    Utilisateur "1" --> "0..*" Commande : passe
    Utilisateur "1" --> "0..*" Avis : rédige

    Commande "1" *-- "1..*" CommandeDetail : compose
    Menu "1" <-- "0..*" CommandeDetail : référence

    Menu "0..*" --> "1..*" Plat : menus_plats
    Menu "0..*" --> "0..*" Theme : menus_themes
    Menu "1" --> "0..*" Avis : reçoit

    Plat "0..*" --> "0..*" Allergene : plats_allergenes
    Plat "0..*" --> "0..*" Regime : plats_regimes
    Plat "0..*" --> "0..*" Theme : plats_themes
```

---

## 2. Visuels Exportés
* Format SVG : `docs/diagrammes/Diagramme-de-classes.svg`
* Format PNG : `docs/diagrammes/Diagramme-de-classes.png`