# Spécifications & Matrice des Endpoints API REST — Vite & Gourmand (P1-03)

> Référentiel des contrats d'interface (OpenAPI / Swagger) pour l'API REST FastAPI.  
> Titre Professionnel Développeur Web et Web Mobile (RNCP 37674).  
> Ce document formalise les routes d'API, les méthodes HTTP, les payloads attendus, les codes retours et le contrôle d'accès (RBAC).

---

## 1. Principes d'Architecture de l'API

- **Préfixe global :** `/api/v1`
- **Format d'échange :** `application/json` (encodage UTF-8)
- **Authentification :** En-tête HTTP standard `Authorization: Bearer <JWT_TOKEN>`
- **Format des erreurs standardisées :**
  ```json
  {
    "detail": "Message explicatif de l'erreur ou validation Pydantic"
  }
  ```

* **Rôles RBAC :** (Role-Based Access Control)
  * **Public** : Accessible sans authentification (Visiteur)
  * **Client** : Utilisateur authentifié standard
  * **Employé** : Personnel du restaurant traiteur
  * **Admin** : Direction du restaurant traiteur

---

## 2. Matrice Globale des Endpoints

| Méthode | URI | Rôle Requis | Description Métier | Code Succès | Erreurs Usuelles | Persistance |
| --- | --- | --- | --- | --- | --- | --- |
| **AUTH & COMPTE** |  |  |  |  |  |  |
| `POST` | `/api/v1/auth/register` | Public | Inscription d'un nouveau compte client | `201 Created` | `400`, `409` | PostgreSQL |
| `POST` | `/api/v1/auth/login` | Public | Authentification et émission du token JWT | `200 OK` | `400`, `401` | PostgreSQL |
| `POST` | `/api/v1/auth/forgot-password` | Public | Demande de réinitialisation de mot de passe | `200 OK` | `422` | PostgreSQL |
| `POST` | `/api/v1/auth/reset-password` | Public | Validation du nouveau mot de passe via token | `200 OK` | `400`, `404` | PostgreSQL |
| `GET` | `/api/v1/users/me` | Client+ | Consultation des informations du profil | `200 OK` | `401` | PostgreSQL |
| `PATCH` | `/api/v1/users/me` | Client+ | Modification des coordonnées personnelles | `200 OK` | `400`, `401` | PostgreSQL |
| `PATCH` | `/api/v1/users/me/password` | Client+ | Modification sécurisée du mot de passe | `200 OK` | `400`, `401` | PostgreSQL |
| **CATALOGUE & HORAIRES** |  |  |  |  |  |  |
| `GET` | `/api/v1/menus` | Public | Liste des menus actifs avec filtres | `200 OK` | `422` | PostgreSQL |
| `GET` | `/api/v1/menus/{id}` | Public | Fiche détaillée d'un menu et ses plats | `200 OK` | `404` | PostgreSQL |
| `GET` | `/api/v1/horaires` | Public | Horaires d'ouverture hebdomadaires | `200 OK` | `500` | PostgreSQL |
| `GET` | `/api/v1/filtres/options` | Public | Référentiels pour filtres (thèmes, régimes) | `200 OK` | `500` | PostgreSQL |
| **TUNNEL DE COMMANDE** |  |  |  |  |  |  |
| `POST` | `/api/v1/commandes/devis` | Public/Client | Simulation calcul prix, remises et km | `200 OK` | `400`, `422` | En mémoire (Service) |
| `POST` | `/api/v1/commandes` | Client | Création d'une commande (panier pré-rempli) | `201 Created` | `400`, `401`, `422` | PostgreSQL |
| `GET` | `/api/v1/commandes` | Client | Historique paginé des commandes du client | `200 OK` | `401` | PostgreSQL |
| `GET` | `/api/v1/commandes/{id}` | Client | Suivi en temps réel de l'état de commande | `200 OK` | `401`, `403`, `404` | PostgreSQL |
| `POST` | `/api/v1/commandes/{id}/annuler` | Client | Annulation par le client (avant acceptation) | `200 OK` | `400`, `403`, `404` | PostgreSQL |
| `GET` | `/api/v1/commandes/{id}/facture` | Client | Téléchargement du PDF de la facture | `200 OK` | `400`, `403`, `404` | PostgreSQL + PDF |
| **CONTACT & AVIS** |  |  |  |  |  |  |
| `POST` | `/api/v1/contact` | Public | Envoi d'un message via le formulaire | `201 Created` | `422` | MongoDB (`contacts`) |
| `POST` | `/api/v1/commandes/{id}/avis` | Client | Dépôt d'un avis suite à commande terminée | `201 Created` | `400`, `403`, `409` | MongoDB (`avis`) |
| `GET` | `/api/v1/avis/public` | Public | Liste des avis approuvés pour la vitrine | `200 OK` | `500` | MongoDB (`avis`) |
| **ESPACE COLLABORATEUR (EMPLOYÉ)** |  |  |  |  |  |  |
| `GET` | `/api/v1/admin/commandes` | Employé/Admin | Tableau de bord et recherche multicritère | `200 OK` | `401`, `403` | PostgreSQL |
| `POST` | `/api/v1/admin/commandes/{id}/accepter` | Employé/Admin | Validation commande et lien de règlement | `200 OK` | `400`, `404` | PostgreSQL |
| `POST` | `/api/v1/admin/commandes/{id}/refuser` | Employé/Admin | Refus avec motif et libération du stock | `200 OK` | `400`, `404` | PostgreSQL |
| `PATCH` | `/api/v1/admin/commandes/{id}/statut` | Employé/Admin | Transition d'état (préparation/livraison) | `200 OK` | `400`, `404` | PostgreSQL |
| `POST` | `/api/v1/admin/commandes/{id}/annuler` | Employé/Admin | Annulation avec contact client tracé | `200 OK` | `400`, `404` | PostgreSQL |
| `POST` | `/api/v1/admin/commandes/{id}/livrer` | Employé/Admin | Confirmation de livraison et encaissement | `200 OK` | `400`, `404` | PostgreSQL |
| `POST` | `/api/v1/admin/commandes/{id}/restitution` | Employé/Admin | Contrôle matériel (conforme / clôture) | `200 OK` | `400`, `404` | PostgreSQL + MongoDB |
| `POST` | `/api/v1/admin/commandes/{id}/litige-materiel` | Employé/Admin | Dépassement > 10j (facture pénalité 600€) | `200 OK` | `400`, `404` | PostgreSQL |
| `POST` | `/api/v1/admin/menus` | Employé/Admin | Ajout d'un menu au catalogue | `201 Created` | `400`, `422` | PostgreSQL |
| `PUT` | `/api/v1/admin/menus/{id}` | Employé/Admin | Mise à jour complète d'un menu | `200 OK` | `400`, `404` | PostgreSQL |
| `DELETE` | `/api/v1/admin/menus/{id}` | Employé/Admin | Suppression logique d'un menu (soft delete) | `200 OK` | `404` | PostgreSQL |
| `GET` | `/api/v1/admin/avis` | Employé/Admin | Liste des avis en attente de modération | `200 OK` | `401`, `403` | MongoDB (`avis`) |
| `PATCH` | `/api/v1/admin/avis/{id}` | Employé/Admin | Modération d'un avis (Approuvé / Rejeté) | `200 OK` | `400`, `404` | MongoDB (`avis`) |
| **ESPACE DIRECTION (ADMINISTRATEUR)** |  |  |  |  |  |  |
| `POST` | `/api/v1/admin/employees` | Admin | Création d'un collaborateur (compte José) | `201 Created` | `400`, `409` | PostgreSQL |
| `PATCH` | `/api/v1/admin/employees/{id}/disable` | Admin | Révocation immédiate d'un employé | `200 OK` | `404` | PostgreSQL |
| `GET` | `/api/v1/admin/stats` | Admin | Indicateurs décisionnels (CA, volumes) | `200 OK` | `401`, `403` | MongoDB (`commandes_stats`) |

---

## 3. Contrats d'Interface Détaillés (Exemples Clés)

### 3.1 Authentification (`POST /api/v1/auth/login`)

* **Corps de la requête (`UserLoginSchema`) :**
```json
{
  "email": "client.durand@example.com",
  "password": "Password123!"
}

```


* **Réponse succès `200 OK` (`TokenResponseSchema`) :**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
  "token_type": "bearer",
  "user": {
    "user_id": 3,
    "email": "client.durand@example.com",
    "prenom": "Marc",
    "nom": "Durand",
    "role": "Client"
  }
}

```



---

### 3.2 Calcul du Devis & Règles Métier (`POST /api/v1/commandes/devis`)

* **Corps de la requête (`QuoteRequestSchema`) :**
```json
{
  "menu_id": 2,
  "quantite_personnes": 25,
  "distance_km": 12.0
}

```


* **Réponse succès `200 OK` (`QuoteResponseSchema`) :**
```json
{
  "menu_id": 2,
  "titre": "Menu Cocktail Signature",
  "prix_unitaire": 32.50,
  "quantite_personnes": 25,
  "sous_total_brut": 812.50,
  "remise_applicable": true,
  "taux_remise": 0.10,
  "montant_remise": 81.25,
  "frais_livraison": 12.08,
  "total_estime_ttc": 743.33
}

```



---

### 3.3 Annulation de Commande par l'Employé (`POST /api/v1/admin/commandes/{id}/annuler`)

* **Corps de la requête (`OrderCancelAuditSchema`) :**
```json
{
  "motif": "Panne de chambre froide empêchant le maintien de la chaîne du froid.",
  "mode_contact": "Téléphone",
  "contact_client_effectue": true
}

```


* **Réponse succès `200 OK` :**
```json
{
  "message": "Commande annulée avec succès, stock restauré et client notifié.",
  "commande_id": 3,
  "statut": "Annulée",
  "stock_restaure": true
}

```



---

### 3.4 Statistiques Décisionnelles Admin (`GET /api/v1/admin/stats?annee=2026&mois=10`)

* **En-tête :** `Authorization: Bearer <TOKEN_ADMIN>`
* **Réponse succès `200 OK` (`DashboardStatsSchema`) :**
```json
{
  "periode": {
    "annee": 2026,
    "mois": 10
  },
  "indicateurs_cles": {
    "total_chiffre_affaires": 960.00,
    "nombre_commandes": 1,
    "panier_moyen": 960.00
  },
  "repartition_par_menu": [
    {
      "menu_id": 1,
      "titre": "Menu Prestige des Grands Jours",
      "commandes_count": 1,
      "portions_vendues": 20,
      "chiffre_affaires": 960.00
    }
  ]
}

```


