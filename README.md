# Vite & Gourmand — Plateforme de Traiteur Événementiel

![Angular](https://img.shields.io/badge/Frontend-Angular_18+-DD0031?style=flat-square&logo=angular&logoColor=white)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI_Python_3.12-009688?style=flat-square&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/SQL-PostgreSQL_18-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![MongoDB](https://img.shields.io/badge/NoSQL-MongoDB_7-47A248?style=flat-square&logo=mongodb&logoColor=white)
![License](https://img.shields.io/badge/ECF-RNCP_37674_Niveau_5-6B2737?style=flat-square)

Solution web fullstack de réservation de menus traiteur événementiel, de simulation automatisée de devis (remises sur volume, frais kilométriques), de suivi logistique de restitution du matériel sous 10 jours et d'administration commerciale, réalisée par **Sébastien BADEL** dans le cadre de l'Évaluation en Cours de Formation (**ECF**) pour le Titre Professionnel **Développeur Web et Web Mobile (RNCP 37674)**.

---

## Liens Officiels & Environnements Déployés

| Ressource | Environnement | URL / Emplacement |
| :--- | :--- | :--- |
| **Application Web (Frontend)** | Vercel (Edge CDN) | [https://vite-gourmand.sebastienbadel.com](https://vite-gourmand.sebastienbadel.com) |
| **API REST (Backend)** | Railway (ASGI) | [https://api-vg.sebastienbadel.com](https://api-vg.sebastienbadel.com) |
| **Documentation Interactive Swagger** | OpenAPI 3.1 | [https://api-vg.sebastienbadel.com/docs](https://api-vg.sebastienbadel.com/docs) |
| **Dépôt GitHub** | Branches `main` & `dev` | [https://github.com/sebbadev/vite-gourmand.git](https://github.com/sebbadev/vite-gourmand.git) |
| **Maquettes & Design System** | Figma | [Voir le prototype Figma](https://www.figma.com/design/Qp6yvBmAQuXyhS004Qgyzi/ECF-Vite-Gourmand?node-id=14-1136&t=xwdcsW3Qnn50xaol-1)  · `docs/design` |
| **Suivi Agile & Backlog** | Workflowy & Git | [Tableau Workflowy](https://workflowy.com/s/vite-gourmand-ecf/hJdChJKacyv8pEzD) · `docs/backlog.md` |

---

## Architecture & Stack Technique

L'application repose sur une architecture **3-tiers découplée** avec **persistance polyglotte** :

- **Frontend (SPA)** : Angular 18+ (Standalone Components, Signals réactifs `signal()` & `computed()`, Reactive Forms typés, Guards & Intercepteurs JWT, SCSS Mobile-First conforme RGAA).
- **Backend (API REST)** : Python 3.12, FastAPI, Uvicorn (ASGI asynchrone), validation stricte Pydantic v2, sécurité JWT (`PyJWT` HS256), hachage natif `bcrypt` (coût 12) et contrôle d'accès RBAC.
- **Base Relationnelle (ACID)** : PostgreSQL 18 via SQLAlchemy 2.0 et migrations Alembic (utilisateurs, catalogue menus/plats, allergènes, commandes, lignes de devis, horaires).
- **Base Orientée Documents (NoSQL)** : MongoDB 7 via le pilote asynchrone `Motor` (messages du formulaire de contact, avis clients modérés et agrégations décisionnelles pour le tableau de bord administrateur).

### Règles de Gestion Implémentées
- **RG-01 (Seuil minimal)** : Blocage de commande si le nombre de convives est inférieur au minimum requis par le menu.
- **RG-02 (Remise volume 10 %)** : Déduction automatique de 10 % sur le total des menus dès que `convives >= minimum + 5`.
- **RG-03 (Frais de livraison)** : Forfait de `5,00 €` + `0,59 € / km` depuis Bordeaux.
- **RG-04 (Matériel de prêt sous 10 jours)** : Suivi de restitution obligatoire avant clôture au statut *Terminée* (pénalité forfaitaire de `600 €`).
- **RG-05 (Cycle d'annulation)** : Annulation autonome par le client autorisée uniquement tant que la commande est au statut *En attente de validation*.

---

## Structure du Projet

```text
vite-gourmand/
├── backend/                        # API REST FastAPI (Python 3.12)
│   ├── alembic/                    # Migrations de schéma SQLAlchemy
│   ├── app/
│   │   ├── core/                   # Configuration (.env), connexions SQL/NoSQL, JWT & RBAC
│   │   ├── models/                 # Entités relationnelles SQLAlchemy
│   │   ├── routers/                # Contrôleurs API REST (/api/v1/...)
│   │   ├── schemas/                # DTOs de validation Pydantic v2
│   │   └── services/               # Moteur métier (tarification, règles de gestion)
│   ├── database/
│   │   ├── create_db.sql           # Script DDL complet PostgreSQL
│   │   ├── fixtures.sql            # Jeu d'essai SQL initial
│   │   └── mongo_fixtures.json     # Jeu d'essai des collections NoSQL
│   ├── tests/                      # Tests unitaires et d'intégration (Pytest)
│   ├── requirements.txt            # Dépendances Python
│   └── seed.py                     # Script automatisé d'initialisation SQL + MongoDB
│
├── frontend/                       # Application SPA Angular 18+
│   ├── public/assets/images/       # Ressources visuelles optimisées (WebP)
│   ├── src/
│   │   ├── app/
│   │   │   ├── core/               # AuthService, Guards, Intercepteur JWT, Modèles TS
│   │   │   ├── features/           # Vues métiers (Catalogue, Panier, Client, Employé, Admin)
│   │   │   └── shared/             # Composants UI réutilisables (Header, Footer, Cartes)
│   │   └── environments/           # Configuration API dev / prod
│   ├── proxy.conf.json             # Proxy de développement (/api/v1 -> localhost:8000)
│   └── package.json                # Dépendances et scripts NPM / Angular CLI
│
├── docs/                           # Documentation technique et fonctionnelle (Source of Truth)
│   ├── api-endpoints.md            # Référentiel des endpoints REST
│   ├── architecture.md             # Dossier d'architecture technique
│   ├── backlog.md                  # Suivi des sprints et critères d'acceptation
│   └── diagrammes/                 # Diagrammes UML (MCD, Classes, Séquences)
│
└── README.md

```

---

## Installation & Lancement en Local

1. Prérequis Système
Assurez-vous de disposer des outils suivants installés sur votre poste :

- **Git (>= 2.40)**
- **Python (3.12 recommandé)**
- **Node.js (>= 20 LTS) & npm (>= 10)**
- **PostgreSQL (>= 15, testé sous PostgreSQL 18)**
- **MongoDB (>= 7.0 en local ou cluster gratuit MongoDB Atlas)**

2. Clonage du Dépôt

```bash
git clone [https://github.com/sebbadev/vite-gourmand.git](https://github.com/sebbadev/vite-gourmand.git)
cd vite-gourmand
```

---


## Crédits Médias & Propriété Intellectuelle

Les ressources visuelles (photographies culinaires des menus et des plats) intégrées dans `frontend/public/assets/images/` ont été optimisées au format **WebP** (*Web Picture format*) exclusivement dans le cadre pédagogique de l'**ECF** (*Évaluation en Cours de Formation* — Titre professionnel Développeur Web et Web Mobile, RNCP 37674).

## Cadre d'utilisation
- **Usage :** Démonstration technique et maquettage fonctionnel non commercial.
- **Sources :** Banques d'images libres de droits (Unsplash / Pexels) et visuels d'illustration de démonstration.
- **Engagement de mise en production réelle :** Avant toute exploitation commerciale publique, l'ensemble des visuels sera remplacé par les photographies officielles commandées par l'entreprise *Vite & Gourmand*.

## Inventaire des actifs (`frontend/public/assets/images/`)
- **Menus (`menus/`) :** `prestige.webp`, `cocktail.webp`, `vegetal.webp`
- **Plats (`plats/`) :** `carpaccio-st-jacques.webp`, `veloute-potimarron.webp`, `salade-quinoa.webp`, `filet-boeuf-morilles.webp`, `pave-saumon.webp`, `curry-lentilles.webp`, `ecrase-truffe.webp`, `poelee-legumes.webp`, `fondant-chocolat.webp`, `tartelette-citron.webp`, `salade-fruits.webp`