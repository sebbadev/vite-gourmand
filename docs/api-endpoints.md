# Matrice des Endpoints API REST — Vite & Gourmand

Référentiel technique des contrats d'interface de l'API (*Application Programming Interface*) RESTful (*Representational State Transfer*) **Vite & Gourmand** (Titre professionnel Développeur Web et Web Mobile — RNCP 37674).
Ce document consigne l'ensemble des points d'accès (*endpoints*), méthodes HTTP (*Hypertext Transfer Protocol*), paramètres de requête (*query parameters*), corps de transfert (*DTOs — Data Transfer Objects*) et contrôles d'accès basés sur les rôles (*RBAC — Role-Based Access Control*).

---

## 1. Vue d'Ensemble & Standards d'Architecture

- **Protocole & Format :** RESTful HTTP/JSON (*JavaScript Object Notation*), conforme OpenAPI 3.1 / Swagger UI sur `/docs` et ReDoc sur `/redoc`.
- **Préfixe global des routes :** `/api/v1` (hors route de santé `GET /`).
- **Mécanisme d'Authentification :** *Bearer Token* JWT (*JSON Web Token* — RFC 7519) signé en HMAC-SHA256 (HS256), compatible avec les requêtes JSON et le formulaire OAuth2 (`x-www-form-urlencoded`).
- **Gestion des Erreurs :** Codes de statut HTTP standards (`200`, `201`, `204`, `400`, `401`, `403`, `404`, `415`, `422`).

---

## 2. Santé du Système (*Health Check*)

| Méthode | Point d'Accès | Rôle Minimum | Corps de Requête | Modèle de Réponse | Statut HTTP | Description Métier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | Public (Visiteur) | — | JSON (`status`, `projet`, `env`, `databases`) | `200 OK` | Vérifie la disponibilité de l'API FastAPI ainsi que la connectivité en temps réel aux bases PostgreSQL (`SELECT 1`) et MongoDB (`ping`). |

---

## 3. Authentification, Profil & Sécurité des Mots de Passe (`/auth`)

| Méthode | Point d'Accès | Rôle Minimum | Corps de Requête (*Request DTO*) | Modèle de Réponse (*Response DTO*) | Statut HTTP | Description Métier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Public (Visiteur) | `UserCreate` (`email`, `password`, `prenom`, `nom`, coordonnées) | `UserResponse` | `201 Created`<br>`400 Bad Request` | Inscription autonome d'un nouveau client avec attribution forcée du rôle `Client` (protection anti-élévation de privilèges) et hachage `bcrypt`. |
| `POST` | `/api/v1/auth/login` | Public (Visiteur) | `LoginRequest` (`email`, `password`) ou formulaire OAuth2 | `Token` (`access_token`, `token_type: "bearer"`) | `200 OK`<br>`401 Unauthorized` | Connexion utilisateur, vérification du hash `bcrypt` et émission du jeton JWT. Protection anti-énumération. |
| `GET` | `/api/v1/auth/me` | Authentifié (`Client`, `Employé`, `Administrateur`) | — *(En-tête `Authorization: Bearer`)* | `UserResponse` | `200 OK`<br>`401 Unauthorized` | Récupération du profil complet de l'utilisateur connecté pour l'hydratation de la SPA (*Single Page Application*) Angular. |
| `PATCH` | `/api/v1/auth/me` | Authentifié (`Client`, `Employé`, `Administrateur`) | `UserUpdate` (`prenom`, `nom`, `telephone`, `adresse`, `code_postal`, `ville`, `pays`) | `UserResponse` | `200 OK`<br>`401 Unauthorized` | Mise à jour partielle des coordonnées personnelles du compte connecté. |
| `PATCH` | `/api/v1/auth/me/password` | Authentifié (`Client`, `Employé`, `Administrateur`) | `ChangePasswordRequest` (`ancien_password`, `nouveau_password`) | `MessageResponse` | `200 OK`<br>`400 Bad Request` | Changement sécurisé du mot de passe depuis l'espace personnel après vérification de l'ancien mot de passe. |
| `POST` | `/api/v1/auth/forgot-password` | Public (Visiteur) | `ForgotPasswordRequest` (`email`) | `MessageResponse` | `200 OK` | Génération d'un jeton JWT temporaire (15 min) de réinitialisation. Réponse `200` systématique (anti-énumération). |
| `POST` | `/api/v1/auth/reset-password` | Public (Visiteur) | `ResetPasswordRequest` (`token`, `nouveau_password`) | `MessageResponse` | `200 OK`<br>`400 Bad Request` | Validation du jeton temporaire et mise à jour du mot de passe haché en base PostgreSQL. |

---

## 4. Catalogue Commercial : Menus & Plats (`/menus`, `/plats`)

| Méthode | Point d'Accès | Rôle Minimum | Paramètres / Corps de Requête | Modèle de Réponse (*Response DTO*) | Statut HTTP | Description Métier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/menus/filtres` | Public (Visiteur) | — | `CatalogueFilters` (`themes`, `regimes`, `allergenes`) | `200 OK` | Fournit les listes de référence pour initialiser les filtres déroulants côté frontend Angular. |
| `GET` | `/api/v1/menus` | Public (Visiteur) | *Query params* : `prix_max`, `nb_personnes`, `theme_id`, `regime_id`, `sans_allergene_id` | `List[MenuListItem]` | `200 OK` | Catalogue public des menus actifs avec filtres combinés temps réel. Conformité stricte des régimes (100 % des plats) et exclusion stricte des allergènes. |
| `GET` | `/api/v1/menus/{menu_id}` | Public (Visiteur) | *Path param* : `menu_id` (`int`) | `MenuDetail` | `200 OK`<br>`404 Not Found` | Fiche détaillée d'un menu avec ses plats associés, allergènes et badges consolidés. |
| `POST` | `/api/v1/menus` | `Employé` / `Administrateur` | `MenuCreate` (`titre`, `prix_par_personne`, `nombre_personnes_min`, `quantite_disponible`, `plat_ids`, `theme_ids`) | `MenuDetail` | `201 Created`<br>`403 Forbidden` | Création d'un nouveau menu dans le catalogue (back-office). |
| `PUT` | `/api/v1/menus/{menu_id}` | `Employé` / `Administrateur` | `MenuUpdate` (mise à jour partielle, `plat_ids`, `theme_ids`) | `MenuDetail` | `200 OK`<br>`404 Not Found` | Modification d'un menu existant et resynchronisation de ses plats et thèmes associés. |
| `DELETE` | `/api/v1/menus/{menu_id}` | `Employé` / `Administrateur` | *Path param* : `menu_id` (`int`) | — | `204 No Content`<br>`404 Not Found` | Suppression logique (*soft delete*) : bascule `is_deleted = True` et `is_active = False` pour préserver l'historique des commandes. |
| `GET` | `/api/v1/plats` | Public (Visiteur) | *Query param* : `type_de_plat` (`Entrée`, `Plat principal`, `Accompagnement`, `Dessert`) | `List[PlatRead]` | `200 OK` | Liste des plats élémentaires avec leurs allergènes, régimes et thèmes associés. |
| `POST` | `/api/v1/plats` | `Employé` / `Administrateur` | `PlatCreate` (`titre`, `type_de_plat`, `allergene_ids`, `regime_ids`, `theme_ids`) | `PlatRead` | `201 Created`<br>`403 Forbidden` | Création d'un nouveau plat et liaison aux référentiels alimentaires. |
| `PUT` | `/api/v1/plats/{plat_id}` | `Employé` / `Administrateur` | `PlatUpdate` | `PlatRead` | `200 OK`<br>`404 Not Found` | Modification d'un plat et de ses associations taxonomiques. |
| `DELETE` | `/api/v1/plats/{plat_id}` | `Employé` / `Administrateur` | *Path param* : `plat_id` (`int`) | — | `204 No Content`<br>`404 Not Found` | Suppression d'un plat du catalogue. |

---

## 5. Tunnel de Commande & Suivi Logistique (`/commandes`)

| Méthode | Point d'Accès | Rôle Minimum | Paramètres / Corps de Requête | Modèle de Réponse (*Response DTO*) | Statut HTTP | Description Métier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/commandes/devis` | Public (Visiteur) | `QuoteRequest` (`items`, `distance_km`) | `QuoteResponse` | `200 OK`<br>`400 Bad Request` | Simulation temps réel du devis panier : tarif unitaire (RG-01), remise volume 10 % dès `min + 5` (RG-02) et frais kilométriques `5,00 € + 0,59 €/km` (RG-03). |
| `POST` | `/api/v1/commandes` | `Client` | `OrderCreate` (`date_prestation`, `heure_livraison`, `adresse_livraison`, `distance_km`, `items`) | `OrderRead` | `201 Created`<br>`400 Bad Request` | Passation de commande ferme, figeage des tarifs, décrémentation des stocks et génération du numéro unique `CMD-AAAA-XXXX`. |
| `GET` | `/api/v1/commandes/me` | `Client` | — | `List[OrderRead]` | `200 OK` | Historique chronologique personnel des commandes passées par le client authentifié. |
| `GET` | `/api/v1/commandes/admin/toutes` | `Employé` / `Administrateur` | *Query params* : `statut`, `actives_uniquement` (`bool`), `client_id` | `List[OrderRead]` (incluant `client`) | `200 OK`<br>`403 Forbidden` | Suivi opérationnel back-office des commandes avec coordonnées client (`OrderClientSummary`), filtre par défaut sur les commandes actives, par statut ou par client. |
| `GET` | `/api/v1/commandes/{id}` | `Client` / `Employé` / `Administrateur` | *Path param* : `id` (`int`) | `OrderRead` | `200 OK`<br>`403 Forbidden` | Suivi détaillé d'une commande avec cloisonnement de sécurité (un client ne peut consulter que ses propres commandes). |
| `PATCH` | `/api/v1/commandes/{id}` | `Client` | `OrderUpdate` (`date_prestation`, `heure_livraison`, `adresse_livraison`, `distance_km`, `items`) | `OrderRead` | `200 OK`<br>`400 Bad Request` | Modification logistique et des quantités avant acceptation (`En attente de validation`), avec blocage du changement de menu et recalcul des tarifs/stocks. |
| `PATCH` | `/api/v1/commandes/{id}/statut` | `Employé` / `Administrateur` | `OrderStatusUpdate` (`nouveau_statut`, `statut_paiement`, `statut_materiel`) | `OrderRead` | `200 OK`<br>`400 Bad Request` | Transition ordonnée du cycle de vie (`Acceptée` $\rightarrow$ `En préparation` $\rightarrow$ `En cours de livraison` $\rightarrow$ `Livrée` $\rightarrow$ `Terminée`), contrôle de clôture (règlement + matériel restitué) et projection asynchrone vers MongoDB `commandes_stats`. |
| `POST` | `/api/v1/commandes/{id}/annuler` | `Client` / `Employé` / `Administrateur` | `OrderCancelRequest` (`motif_annulation`, `mode_contact_annulation`, `contact_client_effectue`) | `OrderRead` | `200 OK`<br>`400 Bad Request` | Annulation autonome client avant acceptation ou annulation employée avec audit de contact obligatoire et restitution automatique des stocks. |

---

## 6. Avis Clients, Messagerie & Horaires (`/avis`, `/contact`, `/horaires`)

| Méthode | Point d'Accès | Rôle Minimum | Paramètres / Corps de Requête | Modèle de Réponse (*Response DTO*) | Statut HTTP | Description Métier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/avis` | Public (Visiteur) | *Query param* : `limit` (`int`) | `List[AvisRead]` | `200 OK` | Récupère les avis clients au statut `Approuvé` depuis MongoDB pour affichage public. |
| `POST` | `/api/v1/commandes/{id}/avis` | `Client` | `AvisCreate` (`qualite`, `service`, `prix`, `description`) | `AvisRead` | `201 Created`<br>`400 Bad Request` | Dépôt d'un avis multicritère (1 à 5) uniquement sur une commande `Terminée` appartenant au client, enregistré au statut `En attente` dans MongoDB. |
| `GET` | `/api/v1/admin/avis` | `Employé` / `Administrateur` | *Query param* : `statut` (`En attente`, `Approuvé`, `Rejeté`) | `List[AvisRead]` | `200 OK`<br>`403 Forbidden` | Liste les avis clients à modérer depuis MongoDB. |
| `PATCH` | `/api/v1/admin/avis/{avis_id}` | `Employé` / `Administrateur` | `AvisModerationUpdate` (`statut`) | `AvisRead` | `200 OK`<br>`404 Not Found` | Validation (`Approuvé`) ou rejet (`Rejeté`) d'un avis client dans MongoDB. |
| `POST` | `/api/v1/contact` | Public (Visiteur) | `ContactCreate` (`nom`, `prenom`, `email`, `telephone`, `objet`, `message`, `rgpd_consent`) | `ContactRead` | `201 Created`<br>`400 Bad Request` | Enregistrement d'un message visiteur dans la collection MongoDB `contacts` avec vérification du consentement RGPD (*Règlement Général sur la Protection des Données*). |
| `GET` | `/api/v1/admin/contacts` | `Employé` / `Administrateur` | — | `List[ContactRead]` | `200 OK`<br>`403 Forbidden` | Consultation des messages de contact reçus dans le back-office. |
| `PATCH` | `/api/v1/admin/contacts/{contact_id}/traite` | `Employé` / `Administrateur` | *Path param* : `contact_id` (`str`) | `ContactRead` | `200 OK`<br>`404 Not Found` | Marque une demande de contact comme traitée (`traite = True`) dans MongoDB. |
| `GET` | `/api/v1/horaires` | Public (Visiteur) | — | `List[HoraireRead]` | `200 OK` | Liste publique des plages horaires d'ouverture du restaurant traiteur (affichée dans le pied de page Angular). |
| `PUT` | `/api/v1/horaires/{horaire_id}` | `Employé` / `Administrateur` | `HoraireUpdate` (`heure_ouverture`, `heure_fermeture`) | `HoraireRead` | `200 OK`<br>`400 Bad Request` | Mise à jour des horaires d'ouverture et de fermeture d'un jour de la semaine. |

---

## 7. Espace Direction : Personnel, Référentiels & Statistiques NoSQL (`/admin`)

| Méthode | Point d'Accès | Rôle Minimum | Paramètres / Corps de Requête | Modèle de Réponse (*Response DTO*) | Statut HTTP | Description Métier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/admin/employees` | `Administrateur` | *Query param* : `include_disabled` (`bool`) | `List[UserResponse]` | `200 OK`<br>`403 Forbidden` | Liste les comptes collaborateurs (`Employé`) actifs et désactivés. |
| `POST` | `/api/v1/admin/employees` | `Administrateur` | `UserCreate` (`email`, `password`, `prenom`, `nom`, coordonnées) | `UserResponse` | `201 Created`<br>`400 Bad Request` | Création d'un compte collaborateur avec rôle fixé à `Employé` (création d'administrateur impossible via l'API). |
| `PATCH` | `/api/v1/admin/employees/{id}/disable` | `Administrateur` | *Path param* : `id` (`int`) | `UserResponse` | `200 OK`<br>`404 Not Found` | Révocation immédiate de l'accès d'un employé par suppression logique (`is_deleted = True`). |
| `POST` | `/api/v1/admin/referentiels/regimes` | `Administrateur` | `RefItemPayload` (`libelle`) | `RefItem` | `201 Created`<br>`400 Bad Request` | Ajout d'un nouveau régime alimentaire dans le référentiel PostgreSQL (`regimes`). |
| `PUT` | `/api/v1/admin/referentiels/regimes/{regime_id}` | `Administrateur` | *Path param* : `regime_id` (`int`) + `RefItemPayload` (`libelle`) | `RefItem` | `200 OK`<br>`404 Not Found` | Modification du libellé d'un régime alimentaire existant. |
| `POST` | `/api/v1/admin/referentiels/themes` | `Administrateur` | `RefItemPayload` (`libelle`) | `RefItem` | `201 Created`<br>`400 Bad Request` | Ajout d'un nouveau thème événementiel dans le référentiel PostgreSQL (`themes`). |
| `PUT` | `/api/v1/admin/referentiels/themes/{theme_id}` | `Administrateur` | *Path param* : `theme_id` (`int`) + `RefItemPayload` (`libelle`) | `RefItem` | `200 OK`<br>`404 Not Found` | Modification du libellé d'un thème événementiel existant. |
| `GET` | `/api/v1/admin/stats` | `Administrateur` | *Query param* : `annee` (`int`, optionnel) | `AdminStatsResponse` | `200 OK`<br>`403 Forbidden` | Pipelines d'agrégation MongoDB (`commandes_stats`) retournant les KPIs (*Key Performance Indicators*) financiers (CA HT/TVA/TTC, panier moyen), le classement des menus (`$unwind`) et l'évolution mensuelle. |

---

## 8. Récapitulatif des Codes de Statut HTTP

- **`200 OK`** : Requête réussie (lecture, mise à jour, simulation de devis).
- **`201 Created`** : Ressource créée avec succès (inscription, commande, menu, plat, avis, message de contact, référentiel).
- **`204 No Content`** : Suppression logique effectuée sans corps de réponse.
- **`400 Bad Request`** : Règle métier non respectée (ex. quantité inférieure au seuil minimal, stock insuffisant, clôture sans paiement/matériel, doublon).
- **`401 Unauthorized`** : Jeton JWT absent, invalide ou expiré.
- **`403 Forbidden`** : Rôle insuffisant (RBAC) ou tentative d'accès à la commande d'un autre client.
- **`404 Not Found`** : Ressource demandée inexistante ou archivée.
- **`422 Unprocessable Entity`** : Échec de validation de format Pydantic (*EmailStr*, types de champs, longueurs minimales/maximales).