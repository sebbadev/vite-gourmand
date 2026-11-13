# Product Backlog — Vite & Gourmand

## 🎯 Description du document

> Document de cadrage du projet Vite & Gourmand (MVP et évolutions futures).
> Référence méthodologique pour le titre professionnel Développeur Web et Web Mobile (RNCP 37674).

Ce carnet recense l'ensemble des besoins en phases & tâches techniques.

Il sert de guide pour les itérations de développement des fonctionnalités du MVP (Minimum Viable Product) et la traçabilité des commits dans Git.

---

### PHASES DU PROJET

## PHASE 0 [P0]: ANALYSE & INITIATION DU PROJET

* P0-00 Document d'initiation projet - demande du client - pdf
* P0-01 Reprise et analyse du cahier des charges - md
* P0-02 Initiation projet / source of truth / project rules
	* initier Workflowy (link in `/docs/references.md`)
	* initier Local project folder (`/backend`, `/frontend`, `/docs`)
	* Git remote / local git init / README / `.gitignore` on main + branch `dev`

* P0-03 Rôles / Diagramme de cas d'utilisation (Mermaid)
	* Visiteur, Client, Employé, Restaurateur (Chef), Administrateur


* P0-04 Parcours des acteurs / diagrammes de séquences (Mermaid)
* P0-05 Matrice de traçabilité des exigences (Exigence client ➔ RG ➔ Solution technique)

## PHASE 1 [P1]: CONCEPTION & ARCHITECTURE

* P1-01 Modélisation relationnelle (PostgreSQL)
	* Schéma relationnel (Tables : Users, Roles, Menus, Plats, Commandes, commande_details, Avis, Factures)
	* Diagramme MCD & MLD (Mermaid)
	* Script DDL `.sql` initial + jeu d'essai (`fixtures.sql`)


* P1-02 Modélisation NoSQL (MongoDB)
	* Collection pour l'historique et statistiques admin (commandes archivées / métriques CA)


* P1-03 Matrice des Endpoints API REST (OpenAPI / Swagger specs)
	* **Auth & Profil :** `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `GET/PUT /api/v1/users/me`
	* **Catalogue public :** `GET /api/v1/menus`, `GET /api/v1/menus/{id}`, `GET /api/v1/filtres` (thèmes, régimes)
	* **Tunnel commande :** `POST /api/v1/commandes` (calcul remises/frais), `GET /api/v1/commandes/suivi/{code}`
	* **Espaces Métier (Employé / Chef / Admin) :**
	`PATCH /api/v1/admin/commandes/{id}/statut`, `POST/PUT /api/v1/admin/menus`, `GET /api/v1/admin/stats` (NoSQL)
	* **Contact & Avis :** `POST /api/v1/contact`, `POST /api/v1/avis`


* P1-04 Choix technologiques argumentés & Architecture globale (document de justification)

## PHASE 2 [P2]: INITIALISATION & SETUP DU PROJET (DEVOPS LOCAL)

* P2-01 Setup environnement local (Git Bash, Sublime Text, `sublime-project` configuré)
* P2-02 Arborescence root, `.gitignore` global (exclusion `venv/`, `node_modules/`, `.env`)
* P2-03 Initialisation `dev` branch & premier commit propre
* P2-04 Fichier `conventions.md` (règles de commits, branches, formatage)

---


## PHASE 3 [P3]: DÉVELOPPEMENT CORE BACKEND (FASTAPI)

* P3-01 Setup environnement Python (`venv`, `requirements.txt`, variables d'environnement `.env`)
* P3-02 Connexion BDD & Migrations
	* Configuration SQLAlchemy (moteur PostgreSQL) + Motor/PyMongo (MongoDB)
	* Initialisation Alembic & première migration
	* Script d'injection des fixtures de test


* P3-03 Sécurité & Authentification
	* Hachage sécurisé des mots de passe avec `bcrypt` natif (remplacement de passlib pour pérennité technique)
    * Génération et validation des tokens JWT avec `PyJWT` (compatible RFC 7519)
    * Dépendances FastAPI & RBAC (contrôle d'accès par rôles : Visiteur, Client, Employé, Administrateur)
    * Endpoints d'authentification (`/auth/login`, `/auth/me`)


* P3-04 Implémentation de la logique métier (Règles de Gestion)
	* Calcul du devis/panier : remise automatique de 10% si quantité $\ge$ seuil
	* Calcul des frais kilométriques de livraison
	* Pénalité forfaitaire matériel (600 € sous 10 jours)


* P3-05 Routes d'API & Validation Pydantic
	* CRUD Menus avec filtres dynamiques (thème, régime, tarif)
	* Cycle de vie de la commande (En attente, Confirmée, En préparation, Livrée, Annulée)
	* Endpoints d'agrégation statistique pour l'Admin (via MongoDB)


* P3-06 Tests unitaires critiques (Pytest sur calculs de prix et permissions)

---


#### PHASE 4 [P4]: DÉVELOPPEMENT CORE FRONTEND (ANGULAR)
* P4-01 Initialisation Angular (CLI, standalone components, SCSS, configuration proxy API) [DONE]
* P4-02 Socle UI, Charte SCSS, Modèles TypeScript & Layout Global
    * Modèles TypeScript (DTOs alignés sur Pydantic dans `core/models/`)
    * Charte graphique "Vite & Gourmand" (tokens SCSS, typographie accessible RGAA)
    * Header / Navbar adaptative selon le rôle & Footer (horaires dynamiques via `GET /api/v1/horaires`)
    * Page d'accueil (`Home` avec avis approuvés via `GET /api/v1/avis`) & Page Contact (`POST /api/v1/contact` + consentement RGPD)
* P4-03 Authentification, Profil & Guards Angular
    * `AuthService` réactif (RxJS `BehaviorSubject` + persistance `localStorage`)
    * Formulaires réactifs (Connexion, Inscription, Mot de passe oublié / réinitialisation)
    * Intercepteur HTTP fonctionnel (`jwtInterceptor`) pour injecter le Bearer Token
    * Route Guards (`authGuard`, `roleGuard` pour isoler `/mon-compte`, `/employe` et `/admin`)
* P4-04 Catalogue, Détail Menu & Filtres dynamiques
    * Affichage des cartes menus (`GET /api/v1/menus`)
    * Filtres combinés temps réel (prix max, nb personnes, thème, régime, exclusion allergènes via `GET /api/v1/menus/filtres`)
    * Page détail d'un menu (`GET /api/v1/menus/{menu_id}`) avec plats associés et badges allergènes/régimes
* P4-05 Tunnel d'achat, Panier & Espace Client
    * `CartService` réactif (RxJS `BehaviorSubject` + persistance `localStorage`)
    * Simulation de devis temps réel (`POST /api/v1/commandes/devis` : RG-01 à RG-03) et validation de commande (`POST /api/v1/commandes`)
    * Espace Client : profil & changement de mot de passe (`PATCH /api/v1/auth/me`, `PATCH /api/v1/auth/me/password`)
    * Suivi de commandes (`GET /api/v1/commandes/me`), modification/annulation avant acceptation et dépôt d'avis (`POST /api/v1/commandes/{id}/avis`)
* P4-06 Interfaces Métier (Back-Office Employé & Admin)
    * Espace Employé : suivi des commandes (`PATCH /statut`), gestion du matériel/litiges (RG-04), CRUD Menus/Plats, modération des avis, horaires et messages de contact
    * Espace Admin : gestion des comptes employés (`GET/POST/PATCH /api/v1/admin/employees`) et tableau de bord analytique NoSQL (`GET /api/v1/admin/stats`)


---


## PHASE 5 [P5]: STABILISATION & DÉPLOIEMENT

* P5-01 Provisioning des bases distantes (ex: Supabase/Neon pour PostgreSQL, MongoDB Atlas)
* P5-02 Déploiement de l'API FastAPI (ex: Render / Railway) + configuration des CORS
* P5-03 Déploiement du client Angular (ex: Vercel / Netlify / Render Static)
* P5-04 Recette technique de bout en bout (Test E2E du tunnel sur environnement de production)
* P5-05 Durcissement sécurité (variables de production, validation OWASP basique, masquage des erreurs d'API)

---


## PHASE 6 [P6]: DOCUMENTATION TECHNIQUE & UTILISATION

* P6-01 `README.md` principal (présentation, stack, liens production)
* P6-02 `/docs/INSTALLATION.md` (guide pas-à-pas pour lancer le projet en local de zéro)
* P6-03 `/docs/MANUEL_UTILISATION.pdf` (ou `.md` exporté) : guide utilisateur avec captures d'écran
* P6-04 Dossier d'architecture finalisé (MCD, diagrammes Mermaid, dictionnaire de données)
* P6-05 Export miroir vers le Google Drive partagé pour les relecteurs non-codeurs

---


## PHASE 7 [P7]: RECETTE FINALE & GÉL DU CODE

* P7-01 Revue de conformité RNCP / Critères du jury (grille de compétences DWWM)
* P7-02 Nettoyage du code (suppression des `console.log`, code mort, formattage `black` / `prettier`)
* P7-03 Tag Git de version finale (`v1.0.0`) sur la branche `main`
* P7-04 Répétition de la démonstration pour l'évaluation orale