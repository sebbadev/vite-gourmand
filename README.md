# Vite & Gourmand — Plateforme de Traiteur Événementiel

![Angular](https://img.shields.io/badge/Frontend-Angular_18+-DD0031?style=flat-square&logo=angular&logoColor=white)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI_Python_3.12-009688?style=flat-square&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/SQL-PostgreSQL_18-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![MongoDB](https://img.shields.io/badge/NoSQL-MongoDB_7-47A248?style=flat-square&logo=mongodb&logoColor=white)
![License](https://img.shields.io/badge/ECF-RNCP_37674_Niveau_5-6B2737?style=flat-square)

Solution web fullstack de réservation de menus traiteur événementiel, de simulation automatisée de devis (remises sur volume, frais kilométriques), de suivi logistique de restitution du matériel sous 10 jours et d'administration commerciale, réalisée par **Sébastien BADEL** dans le cadre de l'Évaluation en Cours de Formation (**ECF**) pour le Titre Professionnel **Développeur Web et Web Mobile (RNCP 37674)**[cite: 1, 4].

---

## Liens Officiels & Environnements Déployés

| Ressource | Environnement | URL / Emplacement |
| :--- | :--- | :--- |
| **Application Web (Frontend)** | Vercel (Edge CDN) | [https://vite-gourmand.sebastienbadel.com](https://vite-gourmand.sebastienbadel.com) |
| **API REST (Backend)** | Railway (ASGI) | [https://api-vg.sebastienbadel.com](https://api-vg.sebastienbadel.com) |
| **Documentation Interactive Swagger** | OpenAPI 3.1 | [https://api-vg.sebastienbadel.com/docs](https://api-vg.sebastienbadel.com/docs) |
| **Dépôt GitHub** | Branches `main` & `dev` | [https://github.com/sebbadev/vite-gourmand.git](https://github.com/sebbadev/vite-gourmand.git) |
| **Maquettes & Design System** | Figma & Git | [Voir le prototype Figma](https://www.figma.com/design/Qp6yvBmAQuXyhS004Qgyzi/ECF-Vite-Gourmand?node-id=14-1136&t=xwdcsW3Qnn50xaol-1) · `docs/design/` |
| **Suivi Agile & Backlog** | Workflowy & Git | [Tableau Workflowy](https://workflowy.com/s/vite-gourmand-ecf/hJdChJKacyv8pEzD) · `docs/backlog.md` |

---

## Architecture & Stack Technique

L'application repose sur une architecture **3-tiers découplée** avec **persistance polyglotte**[cite: 24, 26] :

- **Frontend (SPA)** : Angular 18+ (Standalone Components, Signals réactifs `signal()` & `computed()`, Reactive Forms typés, Guards & Intercepteurs JWT, SCSS Mobile-First conforme RGAA)[cite: 15, 16, 24, 36, 37, 38, 39].
- **Backend (API REST)** : Python 3.12, FastAPI, Uvicorn (ASGI asynchrone), validation stricte Pydantic v2, sécurité JWT (`PyJWT` HS256), hachage natif `bcrypt` (coût 12) et contrôle d'accès RBAC[cite: 30, 31, 32, 42].
- **Base Relationnelle (ACID)** : PostgreSQL 18 via SQLAlchemy 2.0 et migrations Alembic (utilisateurs, catalogue menus/plats, allergènes, commandes, lignes de devis, horaires)[cite: 24, 26, 27, 28].
- **Base Orientée Documents (NoSQL)** : MongoDB 7 via le pilote asynchrone `Motor` (messages du formulaire de contact, avis clients modérés et agrégations décisionnelles pour le tableau de bord administrateur)[cite: 24, 26, 28, 29].

### Règles de Gestion Implémentées
- **RG-01 (Seuil minimal)** : Blocage de commande si le nombre de convives est inférieur au minimum requis par le menu[cite: 9].
- **RG-02 (Remise volume 10 %)** : Déduction automatique de 10 % sur le total des menus dès que `convives >= minimum + 5`[cite: 9].
- **RG-03 (Frais de livraison)** : Forfait de `5,00 €` + `0,59 € / km` depuis Bordeaux[cite: 9].
- **RG-04 (Matériel de prêt sous 10 jours)** : Suivi de restitution obligatoire avant clôture au statut *Terminée* (pénalité forfaitaire de `600 €`)[cite: 9].
- **RG-05 (Cycle d'annulation)** : Annulation autonome par le client autorisée uniquement tant que la commande est au statut *En attente de validation*[cite: 9].

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

### 1. Prérequis Système

Assurez-vous de disposer des outils suivants installés sur votre poste :
- **Git** (`>= 2.40`)
- **Python** (`3.12` recommandé)[cite: 30]
- **Node.js** (`>= 20 LTS`) & **npm** (`>= 10`)
- **PostgreSQL** (`>= 15`, testé sous PostgreSQL 18)[cite: 24]
- **MongoDB** (`>= 7.0` en local ou cluster gratuit MongoDB Atlas)[cite: 24]

---

### 2. Clonage du Dépôt

```bash
git clone [https://github.com/sebbadev/vite-gourmand.git](https://github.com/sebbadev/vite-gourmand.git)
cd vite-gourmand
```

*(Pour basculer sur la branche d'intégration continue si nécessaire : `git checkout dev`)*[cite: 4, 14]

---

### 3. Configuration des Bases de Données Locales

#### A. PostgreSQL
1. Connectez-vous à l'invite interactive PostgreSQL (`psql -U postgres`) et créez la base de données dédiée :
   ```sql
   CREATE DATABASE vite_gourmand;
   \q
   ```
2. Initialisez le schéma relationnel (tables, contraintes et types `ENUM`) à l'aide du script DDL fourni :
   ```bash
   psql -U postgres -d vite_gourmand -f backend/database/create_db.sql
   ```
   *(Alternative : vous pouvez également appliquer le schéma via Alembic à l'étape suivante).*

#### B. MongoDB
Assurez-vous que le service `mongod` est démarré en local sur le port par défaut `27017` (la base `vite_gourmand_nosql` et ses collections `contacts`, `avis`, `commandes_stats` seront créées automatiquement lors de l'injection des fixtures)[cite: 28, 29].

---

### 4. Installation et Démarrage du Backend (FastAPI)

1. **Ouvrir un terminal et se placer dans le dossier `backend/` :**
   ```bash
   cd backend
   ```

2. **Créer et activer l'environnement virtuel Python :**
   - **Sous Windows (Git Bash) :**
     ```bash
     python -m venv venv
     source venv/Scripts/activate
     ```
   - **Sous Windows (PowerShell) :**
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - **Sous Linux / macOS :**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Installer les dépendances Python :**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configurer les variables d'environnement :**
   Créez un fichier `.env` à la racine du dossier `backend/` (`backend/.env`) avec le contenu suivant :
   ```env
   # Application
   PROJECT_NAME="Vite & Gourmand API"
   ENVIRONMENT="development"
   DEBUG=True
   API_V1_STR="/api/v1"

   # Sécurité JWT (générer une clé aléatoire robuste en production)
   SECRET_KEY="cle-secrete-locale-a-remplacer-pour-la-production-vite-gourmand"
   ALGORITHM="HS256"
   ACCESS_TOKEN_EXPIRE_MINUTES=1440

   # Base de données PostgreSQL
   POSTGRES_SERVER="localhost"
   POSTGRES_PORT=5432
   POSTGRES_USER="postgres"
   POSTGRES_PASSWORD="votre_mot_de_passe_postgres"
   POSTGRES_DB="vite_gourmand"

   # Base de données MongoDB
   MONGO_URI="mongodb://localhost:27017"
   MONGO_DB="vite_gourmand_nosql"

   # Origines CORS autorisées
   BACKEND_CORS_ORIGINS=["http://localhost:4200","[http://127.0.0.1:4200](http://127.0.0.1:4200)"]
   ```

   > **Note concernant MongoDB en local sans TLS :** Dans `backend/app/core/database.py`, si votre instance MongoDB locale n'utilise pas TLS/SSL, veillez à ce que la connexion `AsyncIOMotorClient` soit adaptée ou utilisez une URI MongoDB Atlas (`mongodb+srv://...`).

5. **Synchroniser les migrations Alembic et injecter le jeu d'essai (SQL + NoSQL) :**
   ```bash
   alembic upgrade head
   python seed.py
   ```
   *Le script `seed.py` peuple automatiquement les référentiels (régimes, allergènes, thèmes), les horaires, les plats, les menus, les utilisateurs de démonstration (mots de passe hachés avec `bcrypt` coût 12) ainsi que les collections MongoDB (`contacts`, `avis`, `commandes_stats`).*

6. **Lancer le serveur API FastAPI :**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   - **API locale accessible sur :** `http://localhost:8000`
   - **Health Check (SQL + NoSQL) :** `http://localhost:8000/`
   - **Documentation Swagger UI interactive :** `http://localhost:8000/docs`

---

### 5. Installation et Démarrage du Frontend (Angular)

1. **Ouvrir un second terminal à la racine du projet et accéder au dossier `frontend/` :**
   ```bash
   cd frontend
   ```

2. **Installer les dépendances Node.js :**
   ```bash
   npm install
   ```

3. **Démarrer le serveur de développement Angular :**
   ```bash
   npm start
   ```
   *(Cette commande exécute `ng serve` en utilisant `proxy.conf.json` afin de rediriger automatiquement les appels `/api/v1` vers `http://localhost:8000`).*

4. **Accéder à l'application dans votre navigateur :**
   - **URL locale :** [http://localhost:4200](http://localhost:4200)[cite: 33]

---

## Comptes de Démonstration (Jeu d'Essai)

Après exécution de `python seed.py` (ou de `backend/database/fixtures.sql`), les comptes suivants sont disponibles pour tester chaque niveau d'habilitation RBAC :

| Rôle | Email | Mot de passe | Périmètre d'accès |
| :--- | :--- | :--- | :--- |
| **Administrateur** | `jose@vite-gourmand.fr` | `Password123!` | Supervision complète, gestion des employés, statistiques NoSQL[cite: 8] |
| **Administrateur** | `julie@vite-gourmand.fr` | `Password123!` | Supervision complète, gestion des employés, statistiques NoSQL[cite: 8] |
| **Administrateur** | `admin@vite-gourmand.fr` | `Password123!` | Supervision complète, gestion des employés, statistiques NoSQL[cite: 8] |
| **Employé** | `employe@vite-gourmand.fr` | `Password123!` | Gestion des commandes, restitution matériel, catalogue & modération avis[cite: 8] |
| **Client** | `client.durand@example.com` | `Password123!` | Passage de commande, devis, suivi logistique, dépôt d'avis[cite: 8] |
| **Client** | `client.leroy@example.com` | `Password123!` | Passage de commande, devis, suivi logistique, dépôt d'avis[cite: 8] |

---

## Exécution des Tests Automatisés

### Tests Backend (Pytest)
Depuis le dossier `backend/` avec l'environnement virtuel activé :
```bash
pytest -v
```
Couvre notamment les règles de calcul tarifaire (`RG-01` à `RG-03`), la pénalité de restitution matériel (`RG-04`) et le contrôle d'accès par rôles (`RBAC` / `JWT`).

### Build de Production Frontend (Angular)
Depuis le dossier `frontend/` :
```bash
npm run build
```

---

## Crédits Médias & Propriété Intellectuelle

Les ressources visuelles (photographies culinaires des menus et des plats) intégrées dans `frontend/public/assets/images/` ont été optimisées au format **WebP** (*Web Picture format*) exclusivement dans le cadre pédagogique de l'**ECF** (*Évaluation en Cours de Formation* — Titre professionnel Développeur Web et Web Mobile, RNCP 37674)[cite: 51].

### Cadre d'utilisation
- **Usage :** Démonstration technique et maquettage fonctionnel non commercial[cite: 51].
- **Sources :** Banques d'images libres de droits (Unsplash / Pexels) et visuels d'illustration de démonstration[cite: 51].
- **Engagement de mise en production réelle :** Avant toute exploitation commerciale publique, l'ensemble des visuels sera remplacé par les photographies officielles commandées par l'entreprise *Vite & Gourmand*[cite: 51].

### Inventaire des actifs (`frontend/public/assets/images/`)
- **Menus (`menus/`) :** `prestige.webp`, `cocktail.webp`, `vegetal.webp`[cite: 51]
- **Plats (`plats/`) :** `carpaccio-st-jacques.webp`, `veloute-potimarron.webp`, `salade-quinoa.webp`, `filet-boeuf-morilles.webp`, `pave-saumon.webp`, `curry-lentilles.webp`, `ecrase-truffe.webp`, `poelee-legumes.webp`, `fondant-chocolat.webp`, `tartelette-citron.webp`, `salade-fruits.webp`[cite: 51]