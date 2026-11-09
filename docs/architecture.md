# Architecture Globale & Choix Technologiques Argumentés — Vite & Gourmand (P1-04)

> **Projet :** Plateforme de commande traiteur événementiel « Vite & Gourmand »  
> **Référentiel :** Titre Professionnel Développeur Web et Web Mobile (RNCP 37674 - Niveau 5)  
> **Auteur :** Sébastien BADEL (sebbadev)  
> **Date de consolidation :** Novembre 2026  

---

## 1. Vision d'Ensemble & Architecture Système

L'application adopte une architecture logicielle **trois tiers découplée**, garantissant l'indépendance du cycle de vie du client web et de l'API serveur, une scalabilité ciblée et une sécurité renforcée.

```text
[ Client Web SPA ]            [ API RESTful ]                 [ Persistance Polyglotte ]
  Angular 18+                   FastAPI (Python)                PostgreSQL (OLTP)
(Standalone Components) <====> (Async / Pydantic) <===========>   & MongoDB (OLAP / Doc)
  [Front-end]                  [Core Backend]                  [Databases]

```

---


## 2. Matrice Justificative des Choix Technologiques

| Composant | Technologie Retenue | Alternatives Écartées | Justifications Métier & Techniques |
| :--- | :--- | :--- | :--- |
| **Front-end Client** | **Angular 18+** *(Standalone Components, TypeScript, SCSS)* | React, Vue.js | • Architecture d'entreprise structurée nativement en TypeScript (typage strict).<br>• Composants autonomes (*Standalone Components*) allégeant le bundle sans modules lourds.<br>• Système d'injection de dépendances et formulaires réactifs natifs pour la validation stricte des contraintes de commande.<br>• Gestion réactive du panier d'achat via `RxJS BehaviorSubject` et persistance `localStorage`. |
| **Back-end API** | **FastAPI** *(Python 3.12+)* | Django, Flask, Express.js | • Performances asynchrones de premier ordre grâce à `Starlette` et `Uvicorn` (moteur ASGI).<br>• Validation automatique des contrats de données via `Pydantic V2` (réduction drastique des erreurs de typage).<br>• Génération native et dynamique de la documentation interactive OpenAPI (Swagger UI à `/docs` et Redoc à `/redoc`).<br>• Système d'injection de dépendances déclaratif (`Depends`) idéal pour le contrôle d'accès basé sur les rôles (RBAC). |
| **Persistance Transactionnelle** | **PostgreSQL 18** *(Relationnel ACID)* | MySQL, SQLite | • Respect strict des propriétés ACID indispensable pour la facturation et les réservations traiteur.<br>• Support natif des types énumérés personnalisés (`CREATE TYPE ... AS ENUM`) pour sécuriser les machines d'états (statuts de commande, paiement, matériel).<br>• Clés étrangères en cascade pour garantir l'intégrité référentielle des compositions de menus et des plats. |
| **Persistance Analytique & Messages** | **MongoDB 7+** *(NoSQL Document / Moteur PyMongo-Motor)* | Redis, table SQL dénormalisée | • Schéma flexible (*schema-less*) adapté aux messages de contact variés sans migration de schéma.<br>• Moteur d'agrégation décisionnelle performant (`$match`, `$unwind`, `$group`) permettant à l'administrateur de générer des graphiques de chiffre d'affaires et de popularité sans saturer PostgreSQL.<br>• Modération en direct des avis clients sans verrouiller les tables relationnelles de production. |
| **Couche ORM & Migrations** | **SQLAlchemy 2.0** + **Alembic** | Tortoise-ORM, Peewee | • Standard industriel en Python pour le mapping objet-relationnel (ORM).<br>• Style déclaratif 2.0 avec typage explicite (`Mapped[]`).<br>• Gestion rigoureuse des migrations de schéma reproductibles et versionnées avec Git via Alembic. |
| **Authentification & Sécurité** | **JWT** *(JSON Web Tokens)* + **Bcrypt** | Sessions stateful par cookies | • Authentification sans état (*stateless*), parfaitement adaptée au découplage complet entre Angular et l'API.<br>• Hachage salé unidirectionnel des mots de passe avec `bcrypt` (facteur de coût paramétré à 12, conforme aux directives ANSSI).<br>• Cloisonnement granulaire des routes via middleware/dépendance RBAC (`Visiteur`, `Client`, `Employé`, `Administrateur`). |

---

## 3. Justification de la Persistance Polyglotte (PostgreSQL vs MongoDB)

Le choix d'une architecture de données hybride répond à une séparation fonctionnelle nette :

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        API FASTAPI (SERVEUR)                           │
└───────────────────┬────────────────────────────────┬───────────────────┘
                    │                                │
    [Flux Transactionnels / OLTP]        [Flux Analytiques & Messages / OLAP]
                    ▼                                ▼
       ┌────────────────────────┐       ┌────────────────────────┐
       │   POSTGRESQL (ACID)    │       │   MONGODB (DOCUMENTS)  │
       ├────────────────────────┤       ├────────────────────────┤
       │ • Comptes utilisateurs │       │ • Contacts prospects   │
       │ • Catalogue menus/plats│       │ • Avis en modération   │
       │ • Commandes & Devis    │       │ • commandes_stats      │
       │ • Suivi du matériel    │       │   (Reporting décision) │
       │ • Factures & Règlements│       │                        │
       └────────────────────────┘       └────────────────────────┘

```

1. **Isolation des charges (OLTP vs OLAP) :**
Les calculs statistiques de l'administrateur (chiffre d'affaires consolidé, analyse des ventes par trimestre) sollicitent d'importants volumes de données. En déportant ces calculs vers la collection dénormalisée `commandes_stats` dans MongoDB, on garantit que les clients qui passent commande sur PostgreSQL ne subissent aucun ralentissement ou verrou de table (*table locking*).
2. **Cycle de vie des avis et messages :**
Les retours d'expérience et les demandes de contact ont une structure semi-structurée susceptible d'évoluer (ajout d'une note spécifique, pièces jointes ultérieures). MongoDB absorbe ces évolutions sans nécessiter d'altération de schéma SQL (*ALTER TABLE*).

---

## 4. Politique de Sécurité Applicative (OWASP & RGPD)

Conformément aux exigences du client et du standard OWASP Top 10 :

* **Prévention des Injections SQL :** Aucune concaténation de requêtes en chaîne brute. Toutes les interactions SQL s'opèrent via l'ORM SQLAlchemy avec requêtes paramétrées et typage fort Pydantic.
* **Sécurisation des Mots de Passe :** Exigence d'au moins 10 caractères (avec minuscules, majuscules, chiffres et caractères spéciaux). Hachage via `bcrypt` avec sel cryptographique aléatoire. Aucun mot de passe n'est jamais consigné en clair dans les logs ou les emails transactionnels.
* **Protection Cross-Origin (CORS - *Cross-Origin Resource Sharing*) :** Configuration explicite du middleware FastAPI pour restreindre les origines autorisées au domaine du client Angular (`http://localhost:4200` en local, URL Vercel/Render en production).
* **Conformité RGPD :**
* Suppression logique (*Soft Delete*) via le champ `is_deleted` pour permettre l'inactivation d'un compte ou d'un employé tout en préservant l'historique comptable obligatoire.
* Formulaire de contact et d'inscription avec case à cocher explicite de consentement au traitement des données personnelles.
* Émission de factures PDF infalsifiables et horodatées.



---

## 5. Arborescence Globale du Projet

Le projet adopte une organisation en monorepo clair et découplé :

```text
@Vite_Gourmand/
│
├── README.md                           # Présentation du projet, badges et quickstart
├── .gitignore                          # Exclusions strictes (venv, node_modules, .env, admin)
│
├── admin/                              # Espace administration et utilitaires (ignoré par Git)
│
├── docs/                               # Référentiel documentaire (Source of Truth)
│   ├── architecture.md                 # Ce document (P1-04)
│   ├── backlog.md                      # Carnet de bord des phases P0 à P7
│   ├── conventions.md                  # Règles de commits et de branches Git
│   ├── modele-donnees.md               # Schéma relationnel, MCD, ENUMs et NoSQL (P1-01, P1-02)
│   ├── api-endpoints.md                # Matrice des routes d'API et contrats REST (P1-03)
│   ├── tracabilite-exigences.md        # Matrice P0-05 (Exigence ➔ RG ➔ Solution technique)
│   ├── diagrammes/                     # Diagrammes Mermaid, exports SVG et PNG
│   │   └── sequences/                  # Diagrammes de séquence des 4 acteurs (P0-04)
│   └── specs/                          # Spécifications détaillées par acteur
│
├── backend/                            # API REST & Logique Métier (FastAPI / Python)
│   ├── database/                       # Scripts SQL et données de seed
│   │   ├── create_db.sql               # Schéma DDL relationnel PostgreSQL (P1-01)
│   │   ├── fixtures.sql                # Jeu d'essai SQL relationnel (P1-01)
│   │   └── mongo_fixtures.json         # Jeu d'essai NoSQL MongoDB (P1-02)
│   └── app/                            # Code source applicatif
│       ├── models/                     # Entités relationnelles SQLAlchemy
│       ├── core/                       # Configuration, sécurité bcrypt, JWT et RBAC (P3)
│       ├── schemas/                    # DTOs Pydantic de validation (P3)
│       ├── services/                   # Moteur des règles de gestion tarification/commandes (P3)
│       └── routers/                    # Contrôleurs API REST v1 (P3)
│
└── frontend/                           # Application Web SPA (Angular 18+ Standalone) (P4)
    ├── src/
    │   ├── app/
    │   │   ├── core/                   # Guards, Intercepteurs HTTP, Services d'authentification
    │   │   ├── features/               # Modules fonctionnels (Catalogue, Panier, Dashboards)
    │   │   └── shared/                 # Composants réutilisables, pipes et modèles
    │   └── styles.scss                 # Charte graphique et tokens SCSS
    └── package.json

```