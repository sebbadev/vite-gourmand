## 1. Arborescence Globale du Projet

Le projet **Vite & Gourmand** adopte une structure en monorepo découplé, séparant rigoureusement la documentation technique et de cadrage (`/docs`), l'API serveur Python (`/backend`), et le client web Angular (`/frontend`).

```text
vite-et-gourmand/
│
├── .gitignore                      # Exclusion globale (venv, node_modules, .env, dist)
├── README.md                       # Présentation globale, stack, accès rapides
├── mon-projet.sublime-project      # Configuration de l'espace de travail Sublime Text
│
├── docs/                           # Référentiel documentaire (Source of Truth)
│   ├── architecture.md             # Justification stack, flux et arborescence globale
│   ├── backlog.md                  # Carnet produit (Phases P0 à P7) et traçabilité
│   ├── conventions.md              # Normes de commit, gestion des branches et workflow
│   ├── INSTALLATION.md             # Guide d'exécution locale de zéro (back + front + BDDs)
│   ├── MANUEL_UTILISATION.md       # Manuel utilisateur avec rôles de démonstration
│   ├── modele_donnees.md           # Cartographie multicouche et types énumérés
│   ├── tracabilite_exigences.md    # Matrice P0-05 (Exigence ➔ RG ➔ Solution technique)
│   │
│   ├── diagrammes/                 # Exports graphiques (SVG / PNG)
│   │   ├── cas-utilisation-global.png
│   │   ├── diagramme-classes.png
│   │   ├── architecture-3tiers.svg
│   │   └── sequences/              # Diagrammes de séquence par parcours
│   │
│   └── specs/                      # Spécifications détaillées par acteur
│       ├── parcours-visiteur.md
│       ├── parcours-client.md
│       ├── parcours-employe.md
│       └── parcours-administrateur.md
│
├── backend/                        # API REST & Logique Métier (FastAPI / Python)
│   ├── .env.example                # Modèle des variables d'environnement (DB, JWT, Ports)
│   ├── requirements.txt            # Dépendances Python verrouillées
│   │
│   ├── alembic/                    # Gestion des migrations de schéma PostgreSQL
│   │   ├── env.py
│   │   └── versions/
│   │
│   ├── sql/                        # Scripts d'initialisation et jeux d'essai
│   │   ├── create_db.sql           # Schéma DDL relationnel (tables, ENUMs, contraintes)
│   │   └── fixtures.sql            # Données de test initiales (seed data)
│   │
│   ├── app/                        # Code source de l'application FastAPI
│   │   ├── __init__.py
│   │   ├── main.py                 # Point d'entrée FastAPI, middleware CORS, routes
│   │   │
│   │   ├── core/                   # Configuration transverse et sécurité
│   │   │   ├── __init__.py
│   │   │   ├── config.py           # Chargement des variables .env (BaseSettings)
│   │   │   ├── security.py         # Hachage bcrypt des mots de passe
│   │   │   ├── jwt.py              # Encodage, décodage et validation des jetons JWT
│   │   │   └── rbac.py             # Dépendances de vérification des rôles (Admin/Employé)
│   │   │
│   │   ├── database/               # Connexions aux bases de données
│   │   │   ├── __init__.py
│   │   │   ├── session_pg.py       # Session SQLAlchemy pour PostgreSQL (moteur ACID)
│   │   │   └── session_mongo.py    # Client Motor / PyMongo pour MongoDB (NoSQL)
│   │   │
│   │   ├── models/                 # Modèles ORM SQLAlchemy (Entités relationnelles)
│   │   │   ├── __init__.py
│   │   │   ├── user.py             # Entité Utilisateur
│   │   │   ├── menu.py             # Entités Menu, Plat, Allergène, Régime, Thème
│   │   │   ├── order.py            # Entités Commande, CommandeDetail
│   │   │   └── schedule.py         # Entité Horaire
│   │   │
│   │   ├── schemas/                # Schémas DTO Pydantic (Contrats entrées/sorties API)
│   │   │   ├── __init__.py
│   │   │   ├── user_schema.py      # UserCreate, UserRead, TokenResponse
│   │   │   ├── menu_schema.py      # MenuRead, MenuFilterRequest
│   │   │   ├── order_schema.py     # OrderCreate, OrderRead, PriceCalculationResponse
│   │   │   └── contact_schema.py   # ContactCreate, ReviewCreate
│   │   │
│   │   ├── services/               # Moteur des Règles de Gestion (RG) métier
│   │   │   ├── __init__.py
│   │   │   ├── pricing_service.py  # Calculs RG-01 (base), RG-02 (-10%), RG-03 (km)
│   │   │   ├── order_service.py    # Machine d'états et transitions de commandes
│   │   │   ├── material_service.py # Suivi restitution 10j et pénalités 600 €
│   │   │   ├── mail_service.py     # Envois asynchrones d'emails transactionnels
│   │   │   └── pdf_service.py      # Génération dynamique des factures PDF
│   │   │
│   │   └── routers/                # Contrôleurs API REST (Endpoints v1)
│   │       ├── __init__.py
│   │       ├── auth_router.py      # /api/v1/auth (register, login, reset-password)
│   │       ├── user_router.py      # /api/v1/users (profil, modification compte)
│   │       ├── menu_router.py      # /api/v1/menus (catalogue public et filtres)
│   │       ├── order_router.py     # /api/v1/commandes (tunnel, annulation, devis)
│   │       ├── admin_router.py     # /api/v1/admin (RH employés, gestion catalogue)
│   │       ├── stats_router.py     # /api/v1/admin/stats (agrégations analytiques NoSQL)
│   │       └── contact_router.py   # /api/v1/contact et /api/v1/avis (MongoDB)
│   │
│   └── tests/                      # Suite de tests automatisés (Pytest)
│       ├── conftest.py             # Fixtures de test et base SQLite/Postgres éphémère
│       ├── test_pricing.py         # Validation unitaire des calculs de remises et frais
│       ├── test_auth.py            # Tests de validation JWT et permissions RBAC
│       └── test_orders.py          # Tests du cycle de vie des commandes
│
└── frontend/                       # Client Web SPA (Angular Standalone Components)
    ├── package.json                # Dépendances Node.js et scripts de build
    ├── angular.json                # Configuration du projet Angular CLI
    ├── tsconfig.json               # Options de compilation TypeScript
    │
    ├── src/
    │   ├── index.html              # Page hôte unique (SPA)
    │   ├── main.ts                 # Bootstrap de l'application Angular
    │   ├── styles.scss             # Variables globales SCSS (charte Vite & Gourmand)
    │   │
    │   ├── assets/                 # Ressources statiques publiques
    │   │   ├── images/             # Logos, bannières, illustrations
    │   │   └── icons/              # Icônes SVG accessibles
    │   │
    │   └── app/
    │       ├── app.routes.ts       # Table de routage principale (Lazy loading)
    │       ├── app.config.ts       # Fournisseurs d'injection (HttpClient, Interceptors)
    │       │
    │       ├── core/               # Services singleton et sécurité globale
    │       │   ├── guards/
    │       │   │   ├── auth.guard.ts         # Protection connexion requise
    │       │   │   └── role.guard.ts         # Cloisonnement RBAC (/admin, /collaborateur)
    │       │   ├── interceptors/
    │       │   │   ├── jwt.interceptor.ts    # Injection automatique du Bearer Token
    │       │   │   └── error.interceptor.ts  # Capture globale des erreurs HTTP (401, 500)
    │       │   └── services/
    │       │       ├── auth.service.ts       # Gestion login/logout et session utilisateur
    │       │       └── storage.service.ts    # Abstraction du localStorage
    │       │
    │       ├── shared/             # Composants et pipes réutilisables
    │       │   ├── components/
    │       │   │   ├── navbar/               # En-tête responsive adaptatif selon le rôle
    │       │   │   ├── footer/               # Pied de page (horaires, CGV, RGPD)
    │       │   │   └── alert-modal/          # Modales d'alerte et de confirmation
    │       │   └── pipes/
    │       │       ├── price.pipe.ts         # Formatage monétaire en euros
    │       │       └── order-status.pipe.ts  # Traduction et badges couleur des statuts
    │       │
    │       └── features/           # Modules métier autonomes
    │           ├── home/                     # Page d'accueil (vitrine, avis approuvés)
    │           ├── catalog/                  # Catalogue menus et filtres en temps réel
    │           │   ├── catalog-list/
    │           │   ├── catalog-filter/
    │           │   └── menu-detail/
    │           ├── cart-checkout/            # Panier et tunnel de commande
    │           ├── client-space/             # Espace client (suivi horodaté, factures PDF)
    │           ├── employee-space/           # Dashboard collaborateur (commandes, catalogue)
    │           └── admin-space/              # Dashboard direction (analytics NoSQL, personnel)