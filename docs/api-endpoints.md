# Matrice des Endpoints API REST — Vite & Gourmand

> Référentiel technique des contrats d'interface de l'API RESTful **Vite & Gourmand** (Titre professionnel Développeur Web et Web Mobile - RNCP 37674).  
> Ce document consigne l'ensemble des points d'accès (endpoints), méthodes HTTP, paramètres de requête, corps de transfert (DTOs) et contrôles d'accès basés sur les rôles (RBAC).

---

## 1. Vue d'Ensemble & Standards d'Architecture

- **Protocole & Format :** RESTful HTTP/JSON (conforme OpenAPI 3.1 / Swagger UI).
- **Préfixe global des routes :** `/api/v1`
- **Mécanisme d'Authentification :** Bearer Token (JSON Web Token - RFC 7519) signé en HMAC-SHA256 (HS256).
- **Gestion des Erreurs :** Codes de statut HTTP standards (`200`, `201`, `204`, `400`, `401`, `403`, `404`, `422`).

---

## 2. Authentification & Profil Utilisateur (`/auth`)

| Méthode | Point d'Accès | Rôle Minimum | Corps de Requête (Request DTO) | Modèle de Réponse (Response DTO) | Statut HTTP | Description Métier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/login` | Public (Visiteur) | `LoginRequest` (email, password) | `Token` (access_token, token_type: "bearer") | `200 OK`<br>`401 Unauthorized` | Connexion utilisateur, vérification du hash bcrypt et émission du jeton JWT. Protection anti-énumération. |
| `GET` | `/api/v1/auth/me` | Authentifié (Client, Employé, Admin) | — *(En-tête Authorization: Bearer)* | `UserResponse` (user_id, email, prenom, nom, role, coordonnées) | `200 OK`<br>`401 Unauthorized` | Récupération du profil complet de l'utilisateur connecté pour l'hydratation de la SPA Angular. |

---

## 3. Catalogue Commercial & Menus (`/menus`)

| Méthode | Point d'Accès | Rôle Minimum | Paramètres / Corps de Requête | Modèle de Réponse (Response DTO) | Statut HTTP | Description Métier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/menus/filtres` | Public (Visiteur) | — | `CatalogueFilters` (themes, regimes, allergenes) | `200 OK` | Fournit les listes de référence pour initialiser les filtres déroulants (dropdowns) côté frontend Angular. |
| `GET` | `/api/v1/menus` | Public (Visiteur) | Query params :<br>• `prix_max` (float)<br>• `nb_personnes` (int)<br>• `theme_id` (int)<br>• `regime_id` (int)<br>• `sans_allergene_id` (int) | `List[MenuListItem]` (avec badges themes, regimes, allergenes déduits) | `200 OK` | Catalogue public des menus actifs avec filtres combinés temps réel. Conformité stricte pour les régimes (100% des plats) et exclusion stricte des allergènes. |
| `GET` | `/api/v1/menus/{menu_id}` | Public (Visiteur) | Path param : `menu_id` (int) | `MenuDetail` (composition complète des plats, allergènes et badges globaux) | `200 OK`<br>`404 Not Found` | Fiche détaillée d'un menu avant mise au panier ou passation de commande. |
| `POST` | `/api/v1/menus` | Employé / Admin | `MenuCreate` (titre, prix, nb_personnes_min, stock, plat_ids, theme_ids) | `MenuDetail` | `201 Created`<br>`401 / 403` | Création d'un nouveau menu dans le catalogue (back-office). |
| `DELETE` | `/api/v1/menus/{menu_id}` | Employé / Admin | Path param : `menu_id` (int) | — | `204 No Content`<br>`404 Not Found` | Suppression logique (soft delete) : bascule `is_deleted = True` et `is_active = False` pour préserver l'historique des commandes. |

---

## 4. Devis & Logique Métier Panier (`/commandes`)

| Méthode | Point d'Accès | Rôle Minimum | Corps de Requête (Request DTO) | Modèle de Réponse (Response DTO) | Statut HTTP | Description Métier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/commandes/devis` | Public (Visiteur) | `QuoteRequest` (items: [menu_id, quantite], distance_km) | `QuoteResponse` (sous_total_brut, remise_appliquee, frais_livraison, prix_total, eligible_remise) | `200 OK`<br>`400 Bad Request` | Moteur de tarification dynamique :<br>• RG-01 : Montant brut = personnes × prix unitaire (contrôle seuil minimal).<br>• RG-02 : Remise automatique de 10% si quantite ≥ min + 5.<br>• RG-03 : Frais de livraison = 5,00 € + 0,59 € / km. |

---

#### 5. Tunnel de Commande, Logistique & Statistiques NoSQL (`/commandes`, `/admin/stats`)

| Méthode | Point d'Accès | Rôle Minimum | Paramètres / Corps de Requête | Modèle de Réponse (Response DTO) | Statut HTTP | Description Métier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/commandes` | Client | `OrderCreate` (date, heure, adresse, distance, `items`) | `OrderRead` | `201 Created`<br>`400 Bad Request` | Passation de commande ferme, calcul tarifaire (RG-01 à RG-03), décrémentation des stocks et génération du numéro `CMD-AAAA-XXXX`. |
| `GET` | `/api/v1/commandes/me` | Client | — | `List[OrderRead]` | `200 OK` | Historique chronologique personnel des commandes passées par le client connecté. |
| `GET` | `/api/v1/commandes/{id}` | Client / Employé / Admin | Path param : `id` (int) | `OrderRead` | `200 OK`<br>`403 Forbidden` | Suivi détaillé d'une commande avec cloisonnement de sécurité (un client ne voit que ses propres commandes). |
| `PATCH` | `/api/v1/commandes/{id}` | Client | Query params (`date_prestation`, `heure_livraison`, `adresse_livraison`, `distance_km`, `quantite`) et/ou `OrderUpdate` | `OrderRead` | `200 OK`<br>`400 Bad Request` | Modification logistique et des quantités avant acceptation (`En attente de validation`), avec blocage strict du changement de menu et recalcul des tarifs/stocks. |
| `PATCH` | `/api/v1/commandes/{id}/statut` | Employé / Admin | `OrderStatusUpdate` (`nouveau_statut`, `statut_paiement`, `statut_materiel`) | `OrderRead` | `200 OK`<br>`400 Bad Request` | Transition ordonnée du cycle de vie <br>(`Acceptée`  `En préparation`  `En cours de livraison`  `Livrée`  `Terminée`), contrôle de clôture (règlement + matériel restitué) et synchronisation asynchrone vers MongoDB `commandes_stats`. |
| `POST` | `/api/v1/commandes/{id}/annuler` | Client / Employé / Admin | `OrderCancelRequest` (optionnel pour client ; motif, mode contact et confirmation obligatoires pour employé) | `OrderRead` | `200 OK`<br>`400 Bad Request` | Annulation autonome client avant acceptation ou annulation employée avec traçabilité de contact, et restitution automatique des stocks. |
| `GET` | `/api/v1/admin/stats` | Admin | Query param : `annee` (int, optionnel) | `AdminStatsResponse` | `200 OK`<br>`403 Forbidden` | Pipelines d'agrégation MongoDB (`commandes_stats`) retournant les KPIs financiers (CA HT/TVA/TTC, panier moyen), le classement des menus (`$unwind`) et l'évolution mensuelle. |