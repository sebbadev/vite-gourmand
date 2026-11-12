### Matrice des Endpoints API REST — Vite & Gourmand
Référentiel technique des contrats d'interface de l'API RESTful **Vite & Gourmand** (Titre professionnel Développeur Web et Web Mobile - RNCP 37674).  
Ce document consigne l'ensemble des points d'accès (endpoints), méthodes HTTP, paramètres de requête, corps de transfert (DTOs) et contrôles d'accès basés sur les rôles (RBAC).

---

#### 1. Vue d'Ensemble & Standards d'Architecture
* **Protocole & Format :** RESTful HTTP/JSON (conforme OpenAPI 3.1 / Swagger UI sur `/docs`).
* **Préfixe global des routes :** `/api/v1`
* **Mécanisme d'Authentification :** Bearer Token (JSON Web Token - RFC 7519) signé en HMAC-SHA256 (HS256), compatible JSON et formulaire OAuth2 (`x-www-form-urlencoded`).
* **Gestion des Erreurs :** Codes de statut HTTP standards (`200`, `201`, `204`, `400`, `401`, `403`, `404`, `422`).

---

#### 2. Authentification, Profil & Sécurité des Mots de Passe (`/auth`)
| Méthode | Point d'Accès | Rôle Minimum | Corps de Requête (Request DTO) | Modèle de Réponse (Response DTO) | Statut HTTP | Description Métier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Public (Visiteur) | `UserCreate` (`email`, `password`, `prenom`, `nom`, coordonnées) | `UserResponse` | `201 Created`<br>`400 Bad Request` | Inscription autonome d'un nouveau client avec attribution forcée du rôle `Client` (protection anti-élévation de privilèges) et hachage `bcrypt`. |
| `POST` | `/api/v1/auth/login` | Public (Visiteur) | `LoginRequest` (`email`, `password`) ou OAuth2 Form | `Token` (`access_token`, `token_type: "bearer"`) | `200 OK`<br>`401 Unauthorized` | Connexion utilisateur, vérification du hash `bcrypt` et émission du jeton JWT. Protection anti-énumération. |
| `GET` | `/api/v1/auth/me` | Authentifié (Client, Employé, Admin) | — *(En-tête `Authorization: Bearer`)* | `UserResponse` | `200 OK`<br>`401 Unauthorized` | Récupération du profil complet de l'utilisateur connecté pour l'hydratation de la SPA Angular. |
| `PATCH` | `/api/v1/auth/me` | Authentifié (Client, Employé, Admin) | `UserUpdate` (`prenom`, `nom`, `telephone`, `adresse`, `code_postal`, `ville`, `pays`) | `UserResponse` | `200 OK`<br>`401 Unauthorized` | Mise à jour partielle des coordonnées personnelles du compte connecté. |
| `PATCH` | `/api/v1/auth/me/password` | Authentifié (Client, Employé, Admin) | `ChangePasswordRequest` (`ancien_password`, `nouveau_password`) | `MessageResponse` | `200 OK`<br>`400 Bad Request` | Changement sécurisé du mot de passe depuis l'espace personnel après vérification de l'ancien mot de passe. |
| `POST` | `/api/v1/auth/forgot-password` | Public (Visiteur) | `ForgotPasswordRequest` (`email`) | `MessageResponse` | `200 OK` | Génération d'un jeton JWT temporaire (15 min) de réinitialisation. Réponse 200 systématique (anti-énumération). |
| `POST` | `/api/v1/auth/reset-password` | Public (Visiteur) | `ResetPasswordRequest` (`token`, `nouveau_password`) | `MessageResponse` | `200 OK`<br>`400 Bad Request` | Validation du jeton temporaire et mise à jour du mot de passe haché en base PostgreSQL. |

---

#### 3. Catalogue Commercial : Menus & Plats (`/menus`, `/plats`)
| Méthode | Point d'Accès | Rôle Minimum | Paramètres / Corps de Requête | Modèle de Réponse (Response DTO) | Statut HTTP | Description Métier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/menus/filtres` | Public (Visiteur) | — | `CatalogueFilters` (`themes`, `regimes`, `allergenes`) | `200 OK` | Fournit les listes de référence pour initialiser les filtres déroulants côté frontend Angular. |
| `GET` | `/api/v1/menus` | Public (Visiteur) | Query params : `prix_max`, `nb_personnes`, `theme_id`, `regime_id`, `sans_allergene_id` | `List[MenuListItem]` | `200 OK` | Catalogue public des menus actifs avec filtres combinés temps réel. Conformité stricte des régimes (100 % des plats) et exclusion stricte des allergènes. |
| `GET` | `/api/v1/menus/{menu_id}` | Public (Visiteur) | Path param : `menu_id` (int) | `MenuDetail` | `200 OK`<br>`404 Not Found` | Fiche détaillée d'un menu avec ses plats associés, allergènes et badges consolidés. |
| `POST` | `/api/v1/menus` | Employé / Admin | `MenuCreate` (`titre`, `prix`, `nb_personnes_min`, `stock`, `plat_ids`, `theme_ids`) | `MenuDetail` | `201 Created`<br>`403 Forbidden` | Création d'un nouveau menu dans le catalogue (back-office). |
| `PUT` | `/api/v1/menus/{menu_id}` | Employé / Admin | `MenuUpdate` (mise à jour partielle, `plat_ids`, `theme_ids`) | `MenuDetail` | `200 OK`<br>`404 Not Found` | Modification d'un menu existant et resynchronisation de ses plats et thèmes associés. |
| `DELETE` | `/api/v1/menus/{menu_id}` | Employé / Admin | Path param : `menu_id` (int) | — | `204 No Content`<br>`404 Not Found` | Suppression logique (*soft delete*) : bascule `is_deleted = True` et `is_active = False` pour préserver l'historique des commandes. |
| `GET` | `/api/v1/plats` | Public (Visiteur) | Query param : `type_de_plat` (`Entrée`, `Plat principal`, `Accompagnement`, `Dessert`) | `List[PlatRead]` | `200 OK` | Liste des plats élémentaires avec leurs allergènes, régimes et thèmes associés. |
| `POST` | `/api/v1/plats` | Employé / Admin | `PlatCreate` (`titre`, `type_de_plat`, `allergene_ids`, `regime_ids`, `theme_ids`) | `PlatRead` | `201 Created`<br>`403 Forbidden` | Création d'un nouveau plat et liaison aux référentiels alimentaires. |
| `PUT` | `/api/v1/plats/{plat_id}` | Employé / Admin | `PlatUpdate` | `PlatRead` | `200 OK`<br>`404 Not Found` | Modification d'un plat et de ses associations taxonomiques. |
| `DELETE` | `/api/v1/plats/{plat_id}` | Employé / Admin | Path param : `plat_id` (int) | — | `204 No Content`<br>`404 Not Found` | Suppression d'un plat du catalogue. |

---

#### 4. Tunnel de Commande & Suivi Logistique (`/commandes`)
| Méthode | Point d'Accès | Rôle Minimum | Paramètres / Corps de Requête | Modèle de Réponse (Response DTO) | Statut HTTP | Description Métier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/commandes/devis` | Public (Visiteur) | `QuoteRequest` (`items`, `distance_km`) | `QuoteResponse` | `200 OK`<br>`400 Bad Request` | Simulation temps réel du devis panier : tarif unitaire (RG-01), remise volume 10 % dès `min + 5` (RG-02) et frais kilométriques `5,00 € + 0,59 €/km` (RG-03). |
| `POST` | `/api/v1/commandes` | Client | `OrderCreate` (`date_prestation`, `heure_livraison`, `adresse_livraison`, `distance_km`, `items`) | `OrderRead` | `201 Created`<br>`400 Bad Request` | Passation de commande ferme, figeage des tarifs, décrémentation des stocks et génération du numéro unique `CMD-AAAA-XXXX`. |
| `GET` | `/api/v1/commandes/me` | Client | — | `List[OrderRead]` | `200 OK` | Historique chronologique personnel des commandes passées par le client authentifié. |
| `GET` | `/api/v1/commandes/admin/toutes` | Employé / Admin | Query params : `statut`, `actives_uniquement` (bool), `client_id` | `List[OrderRead]` | `200 OK`<br>`403 Forbidden` | Suivi opérationnel back-office des commandes (filtre par défaut sur les commandes non terminées/non annulées, par statut ou par client). |
| `GET` | `/api/v1/commandes/{id}` | Client / Employé / Admin | Path param : `id` (int) | `OrderRead` | `200 OK`<br>`403 Forbidden` | Suivi détaillé d'une commande avec cloisonnement de sécurité (un client ne peut consulter que ses propres commandes). |
| `PATCH` | `/api/v1/commandes/{id}` | Client | Query params (`date_prestation`, `heure_livraison`, `adresse_livraison`, `distance_km`, `quantite`) et/ou `OrderUpdate` | `OrderRead` | `200 OK`<br>`400 Bad Request` | Modification logistique et des quantités avant acceptation (`En attente de validation`), avec blocage du changement de menu et recalcul des tarifs/stocks. |
| `PATCH` | `/api/v1/commandes/{id}/statut` | Employé / Admin | `OrderStatusUpdate` (`nouveau_statut`, `statut_paiement`, `statut_materiel`) | `OrderRead` | `200 OK`<br>`400 Bad Request` | Transition ordonnée du cycle de vie (`Acceptée` -> `En préparation` -> `En cours de livraison` -> `Livrée` -> `Terminée`), contrôle de clôture (règlement + matériel restitué) et projection asynchrone vers MongoDB `commandes_stats`. |
| `POST` | `/api/v1/commandes/{id}/annuler` | Client / Employé / Admin | `OrderCancelRequest` (`motif_annulation`, `mode_contact_annulation`, `contact_client_effectue`) | `OrderRead` | `200 OK`<br>`400 Bad Request` | Annulation autonome client avant acceptation ou annulation employée avec audit de contact obligatoire et restitution automatique des stocks. |

---

#### 5. Avis Clients, Messagerie & Horaires (`/avis`, `/contact`, `/horaires`)
| Méthode | Point d'Accès | Rôle Minimum | Paramètres / Corps de Requête | Modèle de Réponse (Response DTO) | Statut HTTP | Description Métier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/avis` | Public (Visiteur) | Query param : `limit` (int) | `List[AvisRead]` | `200 OK` | Récupère les avis clients au statut `Approuvé` depuis MongoDB pour affichage public. |
| `POST` | `/api/v1/commandes/{id}/avis` | Client | `AvisCreate` (`qualite`, `service`, `prix`, `description`) | `AvisRead` | `201 Created`<br>`400 Bad Request` | Dépôt d'un avis multicritère (1 à 5) uniquement sur une commande `Terminée` appartenant au client, enregistré en statut `En attente` dans MongoDB. |
| `GET` | `/api/v1/admin/avis` | Employé / Admin | Query param : `statut` (`En attente`, `Approuvé`, `Rejeté`) | `List[AvisRead]` | `200 OK`<br>`403 Forbidden` | Liste les avis clients à modérer depuis MongoDB. |
| `PATCH` | `/api/v1/admin/avis/{avis_id}` | Employé / Admin | `AvisModerationUpdate` (`statut`) | `AvisRead` | `200 OK`<br>`404 Not Found` | Validation (`Approuvé`) ou rejet (`Rejeté`) d'un avis client dans MongoDB. |
| `POST` | `/api/v1/contact` | Public (Visiteur) | `ContactCreate` (`nom`, `prenom`, `email`, `telephone`, `objet`, `message`, `rgpd_consent`) | `ContactRead` | `201 Created`<br>`400 Bad Request` | Enregistrement d'un message visiteur dans la collection MongoDB `contacts` avec vérification du consentement RGPD. |
| `GET` | `/api/v1/admin/contacts` | Employé / Admin | — | `List[ContactRead]` | `200 OK`<br>`403 Forbidden` | Consultation des messages de contact reçus dans le back-office. |
| `PATCH` | `/api/v1/admin/contacts/{contact_id}/traite` | Employé / Admin | Path param : `contact_id` (str) | `ContactRead` | `200 OK`<br>`404 Not Found` | Marque une demande de contact comme traitée (`traite = True`) dans MongoDB. |
| `GET` | `/api/v1/horaires` | Public (Visiteur) | — | `List[HoraireRead]` | `200 OK` | Liste publique des plages horaires d'ouverture du restaurant traiteur (affichée dans le footer Angular). |
| `PUT` | `/api/v1/horaires/{horaire_id}` | Employé / Admin | `HoraireUpdate` (`heure_ouverture`, `heure_fermeture`) | `HoraireRead` | `200 OK`<br>`400 Bad Request` | Mise à jour des horaires d'ouverture et de fermeture d'un jour de la semaine. |

---

#### 6. Espace Direction : Personnel & Statistiques NoSQL (`/admin`)
| Méthode | Point d'Accès | Rôle Minimum | Paramètres / Corps de Requête | Modèle de Réponse (Response DTO) | Statut HTTP | Description Métier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/admin/employees` | Admin | Query param : `include_disabled` (bool) | `List[UserResponse]` | `200 OK`<br>`403 Forbidden` | Liste les comptes collaborateurs (`Employé`) actifs et désactivés. |
| `POST` | `/api/v1/admin/employees` | Admin | `UserCreate` (`email`, `password`, `prenom`, `nom`, coordonnées) | `UserResponse` | `201 Created`<br>`400 Bad Request` | Création d'un compte collaborateur avec rôle fixé à `Employé` (création d'admin impossible via l'API). |
| `PATCH` | `/api/v1/admin/employees/{id}/disable` | Admin | Path param : `id` (int) | `UserResponse` | `200 OK`<br>`404 Not Found` | Révocation immédiate de l'accès d'un employé par suppression logique (`is_deleted = True`). |
| `GET` | `/api/v1/admin/stats` | Admin | Query param : `annee` (int, optionnel) | `AdminStatsResponse` | `200 OK`<br>`403 Forbidden` | Pipelines d'agrégation MongoDB (`commandes_stats`) retournant les KPIs financiers (CA HT/TVA/TTC, panier moyen), le classement des menus (`$unwind`) et l'évolution mensuelle. |