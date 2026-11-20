# Modélisation & Cartographie des Données — Vite & Gourmand

> Référentiel technique de conception de la persistance des données pour l'application **Vite & Gourmand** (Titre professionnel Développeur Web et Web Mobile - RNCP 37674).  
> Ce document formalise le schéma relationnel, les énumérations métier, la cartographie logicielle multicouche et la justification de la persistance polyglotte (PostgreSQL + MongoDB).

---

## 1. Diagramme de Classes & Modèle Relationnel (UML / Mermaid)

Ce schéma modélise les entités du domaine, leurs attributs, leurs types énumérés et leurs cardinalités, en conformité avec le script d'initialisation `backend/sql/create_db.sql` et les modèles SQLAlchemy de l'API.

```mermaid
classDiagram
    direction TB

    %% ==========================================
    %% ÉNUMÉRATIONS (Types Métier)
    %% ==========================================
    class UserRole {
        <<enumeration>>
        ADMINISTRATEUR
        EMPLOYE
        CLIENT
    }

    class DishType {
        <<enumeration>>
        ENTREE
        PLAT_PRINCIPAL
        ACCOMPAGNEMENT
        DESSERT
    }

    class OrderStatus {
        <<enumeration>>
        EN_ATTENTE_DE_VALIDATION
        ACCEPTEE
        ANNULEE
        EN_PREPARATION
        EN_COURS_DE_LIVRAISON
        LIVREE
        TERMINEE
    }

    class PaymentStatus {
        <<enumeration>>
        EN_ATTENTE_DE_REGLEMENT
        ANNULEE
        REGLEE
    }

    class Equipment {
        <<enumeration>>
        INCLUS
        NON_INCLUS
        RETOURNE
    }

    class ContactMode {
        <<enumeration>>
        TELEPHONE
        EMAIL
    }

    class ReviewStatus {
        <<enumeration>>
        EN_ATTENTE
        APPROUVE
        REPONDU
        REJETE
    }

    class Rating {
        <<enumeration>>
        CRITIQUE
        A_AMELIORER
        CORRECT
        BIEN
        EXCELLENT
    }

    %% ==========================================
    %% CLASSES DU DOMAINE
    %% ==========================================
    class Utilisateur {
        +int user_id
        +string email
        +string password_hash
        +string nom
        +string prenom
        +string telephone
        +string adresse
        +string code_postal
        +string ville
        +string pays
        +UserRole role
        +datetime created_at
        +datetime updated_at
        +bool is_deleted
    }

    class Menu {
        +int menu_id
        +string titre
        +string description
        +float prix_par_personne
        +int nombre_personnes_min
        +int quantite_disponible
        +string images_url
        +bool is_active
        +datetime created_at
        +datetime updated_at
        +bool is_deleted
    }

    class Plat {
        +int plat_id
        +string titre
        +DishType type_de_plat
        +string images_url
    }

    class Commande {
        +int commande_id
        +string numero_commande
        +int user_id
        +date date_prestation
        +datetime heure_livraison
        +float prix_total
        +float remise_appliquee
        +string adresse_livraison
        +float distance_km
        +float frais_livraison
        +OrderStatus statut
        +datetime date_commande
        +PaymentStatus statut_paiement
        +Equipment statut_materiel
        +string motif_annulation
        +ContactMode mode_contact_annulation
        +bool contact_client_effectue
        +datetime updated_at
        +bool is_deleted
    }

    class CommandeDetail {
        +int detail_id
        +int commande_id
        +int menu_id
        +int quantite
        +float prix_applique
        +datetime created_at
        +datetime updated_at
        +bool is_deleted
    }

    class Avis {
        +int avis_id
        +int user_id
        +int menu_id
        +string description
        +ReviewStatus statut
        +Rating qualite
        +Rating service
        +Rating prix
        +datetime created_at
        +datetime updated_at
        +bool is_deleted
    }

    class Horaire {
        +int horaire_id
        +string jour
        +time heure_ouverture
        +time heure_fermeture
        +datetime created_at
        +datetime updated_at
        +bool is_deleted
    }

    class Theme {
        +int theme_id
        +string libelle
    }

    class Regime {
        +int regime_id
        +string libelle
    }

    class Allergene {
        +int allergene_id
        +string libelle
    }

    %% ==========================================
    %% RELATIONS ET CARDINALITÉS
    %% ==========================================
    Utilisateur "1" --> "0..*" Commande : passe
    Utilisateur "1" --> "0..*" Avis : rédige

    Commande "1" *-- "1..*" CommandeDetail : compose
    Menu "1" <-- "0..*" CommandeDetail : référence

    Menu "0..*" --> "1..*" Plat : menus_plats
    Menu "0..*" --> "0..*" Theme : menus_themes
    Menu "1" --> "0..*" Avis : reçoit

    Plat "0..*" --> "0..*" Allergene : plats_allergenes
    Plat "0..*" --> "0..*" Regime : plats_regimes
    Plat "0..*" --> "0..*" Theme : plats_themes

```

---

## 2. Cartographie Multicouche des Données (Mapping)

Cette matrice assure la cohérence des entités à travers les 4 couches de l'application :

1. **Base relationnelle (PostgreSQL)** : Schéma DDL, contraintes d'intégrité et clés étrangères.
2. **Couche ORM (SQLAlchemy)** : Modèles Python objet-relationnel.
3. **Contrats d'API (Pydantic DTO)** : Validation stricte des entrées et sérialisation des sorties JSON.
4. **Base orientée document (MongoDB)** : Stockage dénormalisé, analytique ou modération directe.

| Entité | Rôle Métier | Table PostgreSQL | Modèle ORM (SQLAlchemy) | Schémas DTO (Pydantic) | Persistance NoSQL (MongoDB) |
| --- | --- | --- | --- | --- | --- |
| **Utilisateur** | Gestion des comptes, authentification JWT et contrôle des accès selon les rôles. | `utilisateurs` | `models.Utilisateur` | `UserBase`, `UserCreate`, `UserRead` | — *(non concerné)* |
| **Menu** | Produit principal du catalogue commercial, gestion des portions et décrémentation des stocks. | `menus` | `models.Menu` | `MenuBase`, `MenuRead` | Référencé sous forme dénormalisée dans `commandes_stats` |
| **Plat** | Composant culinaire élémentaire assemblé dans les menus ; support des régimes et allergènes. | `plats` | `models.Plat` | `PlatBase`, `PlatRead` | — *(non concerné)* |
| **Commande** | Suivi transactionnel, logistique de livraison, caution matériel et audit d'annulation. | `commandes` | `models.Commande` | `CommandeBase`, `CommandeRead` | Projetée au statut `Terminée` dans `commandes_stats` |
| **Détail Commande** *(Ligne Panier)* | Association entre une commande et les menus choisis, avec figeage du prix unitaire facturé. | `commande_details` | `models.CommandeDetail` | `CommandeDetailBase` | Intégré comme tableau imbriqué (`menus: [...]`) dans `commandes_stats` |
| **Avis Client** | Notation multicritère (qualité, service, prix), retour d'expérience et workflow de modération. | `avis` *(miroir / intégrité)* | `models.Avis` | `AvisBase`, `AvisRead` | Collection `avis` *(source de données active et modération en direct)* |
| **Horaire** | Plages horaires d'ouverture et de commande du restaurant traiteur. | `horaires` | `models.Horaire` | `HoraireBase`, `HoraireRead` | — *(non concerné)* |
| **Référentiels** *(Thèmes, Régimes, Allergènes)* | Taxonomie pour la recherche multicritère et la sécurité alimentaire des clients. | `themes`, `regimes`, `allergenes` | `models.Theme`, `models.Regime`, `models.Allergene` | `ThemeBase`, `RegimeBase`, `AllergeneBase` | — *(non concerné)* |
| **Statistiques Décisionnelles** *(Reporting Admin)* | Agrégation des volumes de vente et calculs de CA pour les graphiques administrateur. | — *(aucune requête analytique lourde sur l'OLTP)* | — | `StatsResponse`, `DatasetGraphique` | Collection `commandes_stats` *(pipeline d'agrégation `$match`, `$group`)* |

---

## 3. Référentiel des Types Énumérés (PostgreSQL & Python)

Les types énumérés fixent les machines d'états et garantissent l'intégrité des transitions métier au niveau de la base de données (`CREATE TYPE`) et dans le code Python (`Enum`).

### 3.1 Statuts de Commande (`order_status`)

Gère le cycle de vie séquentiel et logistique de la commande :

* `En attente de validation` : Commande créée par le client, en attente de vérification par l'équipe.
* `Acceptée` : Commande confirmée, lien de paiement émis.
* `Annulée` : Commande annulée (par le client avant validation, ou par le restaurant avec contact obligatoire).
* `En préparation` : Menus en cours de fabrication en cuisine.
* `En cours de livraison` : Prise en charge par le livreur en direction du lieu de prestation.
* `Livrée` : Commande et matériel remis au client.
* `Terminée` : Clôture administrative (livrée, soldée financièrement et matériel restitué).

### 3.2 Statuts de Règlement (`payment_status`)

Découplé du statut logistique pour autoriser le paiement en ligne ou à réception :

* `En attente de règlement` : Paiement non encore encaissé.
* `Réglée` : Règlement validé par carte bancaire (webhook) ou encaissement direct (TPE / espèces).
* `Annulée` : Transaction financière clôturée suite à refus de commande.

### 3.3 Statuts du Matériel Prêté (`equipment`)

Encadre la mise à disposition des équipements de service (chafing dishes, vaisselle) et les clauses CGV :

* `Inclus` : Matériel prêté en attente de restitution (délai légal de 10 jours ouvrés).
* `Non inclus` : Aucun matériel consigné, ou dossier basculé en litige (pénalité forfaitaire de 600 €).
* `Retourné` : Matériel restitué complet et déclaré conforme par l'employé.

### 3.4 Rôles Utilisateurs (`user_role`)

Contrôle d'accès basé sur les rôles (RBAC) :

* `Visiteur` : Rôle implicite non authentifié (consultation catalogue).
* `Client` : Utilisateur standard authentifié (passation de commande, suivi, factures).
* `Employé` : Personnel de service (gestion du catalogue, mise à jour des commandes, modération avis).
* `Administrateur` : Gérant du restaurant (gestion RH des employés, tableaux de bord financiers).

### 3.5 Modération & Avis (`review_status` & `notes`)

* **Statuts d'Avis (`review_status`)** : `En attente`, `Approuvé`, `Répondu`, `Rejeté`.
* **Échelle d'évaluation (`notes`)** : `Critique` (1), `À améliorer` (2), `Correct` (3), `Bien` (4), `Excellent` (5).

---

## 4. Justification de la Persistance Polyglotte (PostgreSQL vs MongoDB)

| Critère de Conception | Base Relationnelle (PostgreSQL) | Base Orientée Document (MongoDB) |
| --- | --- | --- |
| **Rôle applicatif principal** | Transactionnel pur (OLTP) | Analytique & Flexibilité (OLAP / Messages) |
| **Garanties** | Respect strict des propriétés ACID (Atomicité, Cohérence, Isolation, Durabilité). | Modèle de données flexible sans schéma rigide (*schema-less*), requêtes d'agrégation rapides. |
| **Périmètre des données** | Utilisateurs, catalogue commercial, commandes, lignes de facturation, horaires. | Messages de contact, avis clients, documents dénormalisés `commandes_stats`. |
| **Objectif de performance** | Empêcher les réservations incohérentes et garantir la validité des règlements financiers. | Isoler les calculs statistiques lourds (CA par période, popularité) pour ne jamais ralentir les commandes en direct. |

---

## 5. Modélisation NoSQL & Collections MongoDB (P1-02)

Dans le cadre de l'architecture polyglotte, **MongoDB** assure la persistance des données non relationnelles, semi-structurées et analytiques. Ce choix technique découple les flux de consultation/modération et décharge le moteur transactionnel PostgreSQL (OLTP) des requêtes d'agrégation décisionnelles lourdes.

### 5.1 Collection `contacts` (Messages visiteurs & prospects)

Stocke les sollicitations émises via le formulaire de contact public. La flexibilité documentaire permet d'enregistrer des demandes variées (demandes de devis sur mesure, questions allergènes) sans imposer de contraintes de clé étrangère.

#### Schéma Document (JSON Schema)
```json
{
  "_id": "ObjectId",
  "nom": "String (min 2, max 50)",
  "prenom": "String (min 2, max 50)",
  "email": "String (email valide)",
  "telephone": "String (optionnel, 10-15 car)",
  "objet": "String (min 5, max 100)",
  "message": "String (min 10, max 2000)",
  "traite": "Boolean (défaut: false)",
  "created_at": "ISODate"
}
```
Index d'optimisation
```javascript
// Tri chronologique des messages non traités pour le back-office
db.contacts.createIndex({ "traite": 1, "created_at": -1 });
```

### 5.3 Collection commandes_stats (Reporting décisionnel Admin)
Chaque commande franchissant l'état final Terminée dans PostgreSQL est immédiatement dupliquée sous forme dénormalisée dans cette collection. Ce magasin analytique (OLAP) permet au gérant de visualiser les volumes de vente, les paniers moyens et l'évolution du chiffre d'affaires sans impacter la disponibilité de la base transactionnelle.

```json
{
  "_id": "ObjectId",
  "commande_id": "Int (clé primaire PostgreSQL)",
  "numero_commande": "String (ex: CMD-2026-0001)",
  "date_commande": "ISODate",
  "date_prestation": "String (YYYY-MM-DD)",
  "annee": "Int (ex: 2026)",
  "mois": "Int (1 à 12)",
  "semaine": "Int (1 à 52)",
  "montant_ht": "Double",
  "montant_tva": "Double",
  "montant_ttc": "Double",
  "remise_appliquee": "Double",
  "frais_livraison": "Double",
  "distance_km": "Double",
  "menus": [
    {
      "menu_id": "Int",
      "titre": "String",
      "quantite": "Int",
      "prix_unitaire": "Double",
      "total_ligne": "Double"
    }
  ]
}
```
Index d'optimisation
```javascript
// Index pour les filtrages périodiques du tableau de bord
db.commandes_stats.createIndex({ "annee": 1, "mois": 1 });
db.commandes_stats.createIndex({ "menus.menu_id": 1 });
```

### 5.4 Pipeline d'Agrégation Décisionnelle (Exemple d'implémentation Admin)
Exemple de pipeline MongoDB utilisé par l'endpoint GET /api/v1/admin/stats pour calculer le volume de ventes et le chiffre d'affaires consolidé par menu sur une période donnée :

```javascript
db.commandes_stats.aggregate([
  // 1. Filtrer sur l'année et le mois ciblés
  {
    $match: {
      "annee": 2026,
      "mois": 10
    }
  },
  // 2. Déplier le tableau des menus vendus
  {
    $unwind: "$menus"
  },
  // 3. Regrouper par identifiant de menu et calculer les totaux
  {
    $group: {
      _id: "$menus.menu_id",
      titre_menu: { $first: "$menus.titre" },
      total_commandes: { $sum: 1 },
      quantite_totale_portions: { $sum: "$menus.quantite" },
      chiffre_affaires_genere: { $sum: "$menus.total_ligne" }
    }
  },
  // 4. Trier par chiffre d'affaires décroissant
  {
    $sort: { "chiffre_affaires_genere": -1 }
  }
]);
```
