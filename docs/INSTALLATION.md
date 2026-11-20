# Guide d'Installation & Déploiement en Local — Vite & Gourmand

> **Projet :** Plateforme web de traiteur événementiel **Vite & Gourmand**  
> **Référentiel :** Titre Professionnel Développeur Web et Web Mobile (RNCP 37674 — Niveau 5)  
> **Auteur :** Sébastien BADEL (`sebbadev`)  
> **Architecture :** Découplée 3-Tiers (Angular 18+ SPA / API REST FastAPI Python 3.12 / PostgreSQL 18 + MongoDB 7)

Ce guide détaille l'ensemble des étapes nécessaires pour installer, configurer, peupler et exécuter intégralement l'application **Vite & Gourmand** sur un poste de travail local (Windows, Linux ou macOS) à partir de zéro.

---

## Table des Matières

1. [Prérequis Système & Outils](#1-prérequis-système--outils)
2. [Récupération du Code Source](#2-récupération-du-code-source)
3. [Configuration des Bases de Données (PostgreSQL & MongoDB)](#3-configuration-des-bases-de-données-postgresql--mongodb)
4. [Installation & Démarrage du Backend (FastAPI)](#4-installation--démarrage-du-backend-fastapi)
5. [Installation & Démarrage du Frontend (Angular)](#5-installation--démarrage-du-frontend-angular)
6. [Vérification & Comptes de Démonstration](#6-vérification--comptes-de-démonstration)
7. [Exécution des Tests Automatisés](#7-exécution-des-tests-automatisés)
8. [Dépannage & Résolution des Problèmes Fréquents](#8-dépannage--résolution-des-problèmes-fréquents)

---

## 1. Prérequis Système & Outils

Avant de démarrer l'installation, assurez-vous que les logiciels suivants sont installés et accessibles dans le `PATH` de votre système :

| Outil / Service | Version Recommandée | Vérification dans le terminal | Rôle dans le projet |
| :--- | :--- | :--- | :--- |
| **Git** | `>= 2.40` | `git --version` | Clonage et gestion des branches (`main`, `dev`) |
| **Python** | `3.12` | `python --version` | Exécution du serveur d'API FastAPI & scripts |
| **Node.js** | `>= 20 LTS` | `node -v` | Environnement d'exécution Angular CLI |
| **npm** | `>= 10.0` | `npm -v` | Gestionnaire de paquets frontend |
| **PostgreSQL** | `>= 15` (testé sous `18`) | `psql --version` | Persistance relationnelle ACID (commandes, menus, users) |
| **MongoDB** | `>= 7.0` (local ou Atlas) | `mongod --version` | Persistance NoSQL (avis, contacts, statistiques admin) |

---

## 2. Récupération du Code Source

1. **Ouvrez un terminal** (Git Bash sous Windows, Terminal sous Linux/macOS) et clonez le dépôt officiel :
   ```bash
   git clone https://github.com/sebbadev/vite-gourmand.git
   cd vite-gourmand
   ```

2. **Sélection de la branche :**
   - Par défaut, le dépôt s'ouvre sur la branche stable de production (`main`).
   - Pour travailler ou tester les dernières évolutions d'intégration continue, basculez sur `dev` :
     ```bash
     git checkout dev
     ```

---

## 3. Configuration des Bases de Données (PostgreSQL & MongoDB)

L'application repose sur une **persistance polyglotte** nécessitant deux moteurs de bases de données actifs simultanément.

### 3.1. Initialisation de PostgreSQL (Base Relationnelle)

1. **Connectez-vous au serveur PostgreSQL local** avec l'utilisateur administrateur `postgres` :
   ```bash
   psql -U postgres
   ```

2. **Créez la base de données `vite_gourmand` :**
   ```sql
   CREATE DATABASE vite_gourmand;
   \q
   ```

3. **Créez le schéma relationnel (10 tables principales, 5 tables de liaison et 8 types `ENUM`) :**
   Exécutez le script DDL fourni dans le dépôt depuis la racine du projet :
   ```bash
   psql -U postgres -d vite_gourmand -f backend/database/create_db.sql
   ```
   *(Note : ce schéma est strictement synchronisé avec les modèles SQLAlchemy et la migration Alembic).*

### 3.2. Préparation de MongoDB (Base Orientée Documents)

Deux options s'offrent à vous pour la base NoSQL :

* **Option A — Instance MongoDB locale :**
  Assurez-vous que le service `mongod` est démarré sur le port standard `27017`. La base `vite_gourmand_nosql` et ses 3 collections (`contacts`, `avis`, `commandes_stats`) seront créées automatiquement à l'étape suivante.
* **Option B — Cluster Cloud MongoDB Atlas (recommandé si vous n'avez pas installé `mongod` en local) :**
  Utilisez l'URI de connexion TLS fournie par MongoDB Atlas (`mongodb+srv://<utilisateur>:<mot_de_passe>@<cluster>.mongodb.net/?retryWrites=true&w=majority`).

---

## 4. Installation & Démarrage du Backend (FastAPI)

### 4.1. Création de l'environnement virtuel Python

1. **Placez-vous dans le dossier `backend/` :**
   ```bash
   cd backend
   ```

2. **Créez l'environnement virtuel isolé (`venv`) :**
   ```bash
   python -m venv venv
   ```

3. **Activez l'environnement virtuel selon votre système d'exploitation :**
   - **Windows (Git Bash) :**
     ```bash
     source venv/Scripts/activate
     ```
   - **Windows (PowerShell) :**
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS :**
     ```bash
     source venv/bin/activate
     ```
   *(Le préfixe `(venv)` doit apparaître au début de votre invite de commande).*

### 4.2. Installation des dépendances Python

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4.3. Configuration des variables d'environnement (`.env`)

1. **Copiez le fichier modèle `.env.example` vers `.env` :**
   ```bash
   cp .env.example .env
   ```

2. **Éditez le fichier `backend/.env`** et renseignez votre mot de passe PostgreSQL ainsi que votre URI MongoDB :
   ```env
   # --- Métadonnées Application ---
   PROJECT_NAME="Vite & Gourmand API"
   ENVIRONMENT="development"
   DEBUG=True
   API_V1_STR="/api/v1"

   # --- Sécurité & Authentification JWT ---
   SECRET_KEY="cle-secrete-locale-de-developpement-vite-gourmand-2026"
   ALGORITHM="HS256"
   ACCESS_TOKEN_EXPIRE_MINUTES=1440

   # --- Base de données Relationnelle (PostgreSQL) ---
   POSTGRES_SERVER="localhost"
   POSTGRES_PORT=5432
   POSTGRES_USER="postgres"
   POSTGRES_PASSWORD="votre_mot_de_passe_postgres"
   POSTGRES_DB="vite_gourmand"

   # --- Base de données Orientée Documents (MongoDB) ---
   MONGO_URI="mongodb://localhost:27017"
   MONGO_DB="vite_gourmand_nosql"

   # --- Origines CORS Autorisées ---
   BACKEND_CORS_ORIGINS=["http://localhost:4200","http://127.0.0.1:4200"]
   ```

> **Important (Connexion MongoDB locale sans SSL/TLS) :**  
> Dans `backend/app/core/database.py`, le client `AsyncIOMotorClient` est configuré par défaut avec `tls=True` pour la production MongoDB Atlas. Si vous utilisez une instance **MongoDB locale sans certificat TLS** (`mongodb://localhost:27017`), veillez à passer `tls=False` (ou à conditionner `tls` selon le préfixe `mongodb+srv://`, comme implémenté dans `seed.py`).

### 4.4. Migrations Alembic & Injection du Jeu d'Essai (SQL + NoSQL)

1. **Synchronisez l'état des migrations Alembic :**
   ```bash
   alembic stamp head
   ```
   *(Utilisez `alembic stamp head` si vous avez déjà exécuté `create_db.sql`, ou `alembic upgrade head` pour appliquer les migrations).*

2. **Exécutez le script d'initialisation complète (`seed.py`) :**
   ```bash
   python seed.py
   ```
   Ce script automatisé :
   - Insère les référentiels alimentaires (`6 régimes`, `10 allergènes`, `5 thèmes`) et les horaires du lundi au dimanche.
   - Crée les `11 plats` et les `3 menus` composés avec leurs liaisons relationnelles.
   - Crée les `6 utilisateurs` de démonstration avec hachage `bcrypt` natif (coût 12).
   - Insère `3 commandes` représentatives (*Terminée*, *Acceptée*, *Annulée*) et réaligne les séquences PostgreSQL.
   - Peuple les collections MongoDB (`contacts`, `avis`, `commandes_stats`) depuis `backend/database/mongo_fixtures.json`.

### 4.5. Lancement du serveur Uvicorn

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Le serveur API est désormais opérationnel :
- **Point d'entrée & Health Check (SQL + NoSQL) :** [http://localhost:8000/](http://localhost:8000/)
- **Documentation Interactive Swagger UI :** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Documentation ReDoc :** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 5. Installation & Démarrage du Frontend (Angular)

Laissez le terminal du backend actif et **ouvrez un second terminal** à la racine du projet (`vite-gourmand/`).

### 5.1. Installation des modules Node.js

```bash
cd frontend
npm install
```

### 5.2. Configuration du Proxy de Développement

Aucune configuration manuelle n'est requise :
- En mode développement (`environment.ts`), Angular adresse ses requêtes vers `/api/v1`.
- Le fichier `frontend/proxy.conf.json` intercepte automatiquement les appels `/api` et les redirige vers `http://127.0.0.1:8000`, éliminant tout blocage CORS en local.

### 5.3. Démarrage du serveur de développement Angular

```bash
npm start
```

Une fois la compilation terminée, ouvrez votre navigateur à l'adresse :
- **Interface Web Locale :** [http://localhost:4200](http://localhost:4200)

---

## 6. Vérification & Comptes de Démonstration

### 6.1. Contrôle de Santé (*Health Check*)
Accédez à [http://localhost:8000/](http://localhost:8000/). La réponse JSON doit confirmer la connexion aux deux bases :
```json
{
  "status": "online",
  "projet": "Vite & Gourmand API",
  "env": "development",
  "databases": {
    "postgresql": "connected",
    "mongodb": "connected"
  }
}
```

### 6.2. Comptes Utilisateurs Pré-chargés

Tous les comptes du jeu d'essai partagent le même mot de passe sécurisé : **`Password123!`**

| Rôle RBAC | Titulaire | Adresse Email | URL d'accès dédiée |
| :--- | :--- | :--- | :--- |
| **Administrateur** | José (Co-fondateur) | `jose@vite-gourmand.fr` | `/admin` et `/employe` |
| **Administrateur** | Julie (Co-fondatrice) | `julie@vite-gourmand.fr` | `/admin` et `/employe` |
| **Administrateur** | Sophie (Directrice) | `admin@vite-gourmand.fr` | `/admin` et `/employe` |
| **Employé** | Henry (Collaborateur) | `employe@vite-gourmand.fr` | `/employe` |
| **Client** | Marc Durand | `client.durand@example.com` | `/mon-compte` |
| **Client** | Claire Leroy | `client.leroy@example.com` | `/mon-compte` |

---

## 7. Exécution des Tests Automatisés

### 7.1. Tests Unitaires & Permissions Backend (Pytest)
Dans le dossier `backend/` avec l'environnement `(venv)` activé :
```bash
pytest -v
```
Cette suite valide :
- Le calcul tarifaire de base (`RG-01`), la remise volume de 10 % (`RG-02`) et les frais kilométriques (`RG-03`).
- Le calcul de pénalité forfaitaire de `600 €` en cas de non-restitution du matériel sous 10 jours (`RG-04`).
- L'étanchéité du contrôle d'accès par rôles (`401 Unauthorized` et `403 Forbidden`).

### 7.2. Vérification du Build de Production Frontend
Dans le dossier `frontend/` :
```bash
npm run build
```
Génère le bundle optimisé dans `frontend/dist/frontend/browser`.

---

## 8. Dépannage & Résolution des Problèmes Fréquents

| Symptôme / Erreur | Cause Probable | Solution |
| :--- | :--- | :--- |
| `bash: psql: command not found` (Windows) | Le dossier `bin` de PostgreSQL n'est pas dans le `PATH` Git Bash. | Exécutez `export PATH=$PATH:"/c/Program Files/PostgreSQL/18/bin"` (adaptez le numéro de version `16`, `17` ou `18`). |
| `ModuleNotFoundError: No module named 'app'` | `uvicorn` est lancé depuis le mauvais répertoire. | Placez-vous impérativement dans `vite-gourmand/backend/` avant de lancer `uvicorn app.main:app --reload`. |
| `ServerSelectionTimeoutError` sur MongoDB | MongoDB local tourne sans TLS alors que `database.py` a `tls=True`. | Dans `backend/app/core/database.py`, passez `tls=False` pour une instance locale `mongodb://localhost:27017`, ou utilisez une URI Atlas `mongodb+srv://`. |
| `Address already in use` (Port 8000 ou 4200) | Un ancien processus occupe déjà le port. | Lancez le backend sur un autre port (`--port 8001` en adaptant `proxy.conf.json`) ou fermez le terminal précédent. |
| Erreur `422 Unprocessable Entity` à l'inscription | Le mot de passe ne respecte pas la politique de sécurité. | Saisissez au moins **10 caractères** incluant 1 majuscule, 1 minuscule, 1 chiffre et 1 caractère spécial. |