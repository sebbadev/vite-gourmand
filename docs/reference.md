# Références & Livrables Officiels — Vite & Gourmand

> Référentiel centralisé des environnements déployés, dépôts de code, maquettes, outils de pilotage Agile et livrables documentaires (Titre Professionnel Développeur Web et Web Mobile — RNCP 37674).

---

## 1. Liens Officiels & Environnements (Section 1.2)

| Ressource | Environnement / Plateforme | Lien d'Accès |
| :--- | :--- | :--- |
| **Application Web (Frontend Angular)** | Production (Vercel) | [https://vite-gourmand.sebastienbadel.com](https://vite-gourmand.sebastienbadel.com) |
| **API REST (Backend FastAPI)** | Production (Railway) | [https://api-vg.sebastienbadel.com](https://api-vg.sebastienbadel.com) |
| **Documentation Interactive Swagger** | OpenAPI 3.1 | [https://api-vg.sebastienbadel.com/docs](https://api-vg.sebastienbadel.com/docs) |
| **Dépôt GitHub du Projet** | Branches `main` (Prod) & `dev` | [https://github.com/sebbadev/vite-gourmand.git](https://github.com/sebbadev/vite-gourmand.git) |
| **Maquettes, Wireframes & UI Kit** | Figma & Git (`docs/design/`) | [Consulter le projet Figma](https://www.figma.com/design/Qp6yvBmAQuXyhS004Qgyzi/ECF-Vite-Gourmand?node-id=14-1136&t=xwdcsW3Qnn50xaol-1) |
| **Suivi de Projet & Backlog Agile** | Workflowy | [Consulter l'espace Workflowy](https://workflowy.com/s/vite-gourmand-ecf/hJdChJKacyv8pEzD) |
| **Dossier Documentaire & Livrables** | Google Drive Partagé | [Ouvrir le dossier Google Drive](https://drive.google.com/drive/folders/18lTddW0OCA-YL5zPOPr9bbznUrEzcNyJ?usp=drive_link) |

---

## 2. Organisation du Dépôt Git (`docs/` & Code Source)

L'ensemble de la documentation technique et fonctionnelle est versionné dans le dépôt GitHub sous `docs/` :

* **Présentation & Installation Locale :**
  * `README.md` (à la racine du dépôt) : Présentation du projet, stack technique, procédure complète d'installation locale (PostgreSQL, MongoDB, FastAPI, Angular) et comptes de démonstration.
  * `backend/.env.example` : Modèle des variables d'environnement requises pour l'API.
* **Livrables PDF de Certification :**
  * `docs/Dossier-Synthese-Vite-et-Gourmand.pdf` : Dossier complet d'architecture, sécurité, recette E2E et bilan projet.
  * `docs/Manuel-Utilisation-Vite-et-Gourmand.pdf` : Guide d'utilisation détaillé par rôle (Visiteur, Client, Employé, Administrateur) et identifiants de test.
* **Cahier des Charges & Suivi Agile :**
  * `docs/cahier de charges - liste.md` & `docs/cahier des charges-fonctionnel et technique.md`
  * `docs/backlog.md` & `docs/changelog.md`
  * `docs/tracabilite-exigences.md`
* **Architecture, Base de Données & API :**
  * `docs/architecture.md` : Choix technologiques argumentés, sécurité OWASP/RGPD et arborescence globale.
  * `docs/modele-donnees.md` : Modèle Conceptuel de Données (MCD/MLD), types `ENUM` et schémas NoSQL MongoDB.
  * `docs/api-endpoints.md` : Référentiel des endpoints REST `/api/v1/...`.
  * `backend/database/create_db.sql`, `backend/database/fixtures.sql`, `backend/database/mongo_fixtures.json`, `backend/seed.py`.
* **Conception UI/UX & Modélisation UML :**
  * `docs/design/` : Charte graphique, UI Kit, wireframes et mockups Desktop/Mobile (`.svg`).
  * `docs/diagrammes/` : Diagramme de classes, MCD et diagrammes de séquence par acteur (`.png` / `.svg`).
  * `docs/specs/` : Spécifications fonctionnelles détaillées (`parcours_visiteur.md`, `parcours_client.md`, `parcours_employe.md`, `parcours_administrateur.md`).

---

## 3. Dossier Documentaire Partagé (Google Drive)

Le dossier Google Drive partagé constitue le miroir documentaire destiné aux relecteurs et membres du jury :

* **Cahier de Charges :** Mission originale client (`.pdf`), reprise et analyse des exigences, spécifications fonctionnelles et techniques.
* **Documents Techniques & Synthèse :** Dossier de synthèse final (`.pdf`), choix technologiques, documentation de gestion de projet, guide d'installation locale et documentation de déploiement.
* **Conception Graphique :** Charte graphique, wireframes, mockups haute fidélité et lien Figma.
* **Diagrammes & Base de Données :** Diagrammes UML (cas d'utilisation, séquences, classes, MCD) et scripts SQL (`create_db.sql`, `fixtures.sql`).
* **Support Utilisateur :** Manuel d'utilisation complet (`Manuel-Utilisation-Vite-et-Gourmand.pdf`).

---

## 4. Gestion de Projet Agile (Workflowy)

Le pilotage opérationnel repose sur une arborescence dynamique synchronisée avec `docs/backlog.md` et les commits Git :

* **Vue globale & Tags (`#todo`, `#wip`, `#done`, `#blocked`) :** [https://workflowy.com/s/vite-gourmand-ecf/hJdChJKacyv8pEzD](https://workflowy.com/s/vite-gourmand-ecf/hJdChJKacyv8pEzD)
* **Sprint Board :** [https://workflowy.com/s/sprint-board/VhgWtXFMsKbuZnur](https://workflowy.com/s/sprint-board/VhgWtXFMsKbuZnur)
  * **In Progress :** [https://workflowy.com/s/in-progress/QTwvd2oHNnllp7pR](https://workflowy.com/s/in-progress/QTwvd2oHNnllp7pR) (tâches en cours de développement)
  * **Next :** [https://workflowy.com/s/next/wrg4uyYT3YL1NJDO](https://workflowy.com/s/next/wrg4uyYT3YL1NJDO) (prochaines tâches planifiées)
  * **Backlog Statique :** [https://workflowy.com/s/backlog/zkvhbzILz8Nkb5Kd](https://workflowy.com/s/backlog/zkvhbzILz8Nkb5Kd) (référentiel de traçabilité des commits)