# Parcours Administrateur — Spécifications & Séquences

> L'acteur Administrateur possède l'ensemble des privilèges du rôle Employé, avec en complément la gestion des accès du personnel et le pilotage analytique / décisionnel.

---
=========================================================================================================
Parcours 1 : Création d'un compte Employé
=========================================================================================================


1. Règles et données métier
*   Données requises : Email (identifiant unique), mot de passe temporaire initial, nom, prénom.

*   Attribution du rôle : Rôle fixé obligatoirement à `Employé` (`user_role.EMPLOYE`).

*   Sécurité & Notification : L'employé reçoit un email de bienvenue confirmant l'activation de son compte, 
    sans mention de son mot de passe en clair (bonne pratique de sécurité).

*   Règle stricte : Aucun compte `Administrateur` ne peut être créé via l'application.

2. Diagramme de séquence Mermaid
```mermaid
sequenceDiagram
    autonumber
    actor Admin as Administrateur
    participant Front as Interface Admin (Back-office)
    participant API as Serveur API
    participant BDD as Base de Données (PostgreSQL)
    participant Mail as Service Email

    Admin ->> Front: Accéder à "Gestion du personnel"
    Admin ->> Front: Saisir formulaire (nom, prenom, email, mot_de_passe)
    Admin ->> Front: Cliquer sur "Créer le compte employé"

    Front ->> API: POST /api/v1/admin/employees (nom, prenom, email, password) (Header: Bearer Token)
    API ->> API: VerifierRoleAdmin(token)

    API ->> BDD: VerifierEmailExistant(email)
    BDD -->> API: EmailDisponible (null)

    API ->> API: HasherMotDePasse(password)
    API ->> BDD: InsererUtilisateur(email, hash, nom, prenom, role='Employé')
    BDD -->> API: EmployeCree(user_id)

    API ->> Mail: EnvoyerNotificationCreationCompte(email, nom, prenom)
    Note over Mail: Email de bienvenue sans le mot de passe en clair
    Mail -->> API: EmailEnvoye

    API -->> Front: 201 Created (employe_id, email, role)
    Front -->> Admin: Notification succès ("Compte employé créé avec succès")
```

---
=========================================================================================================
Parcours 2 : Désactivation d'un compte Employé (Révocation d'accès)
=========================================================================================================

1. Règles et données métier
*   Gestion des départs : Rendre un compte employé immédiatement inutilisable suite à un départ de l'entreprise.

*   Suppression logique (Soft Delete) : L'enregistrement n'est pas purgé physiquement pour conserver 
    l'intégrité référentielle des commandes et avis passés (`is_deleted = true`).

*   Révocation de session : Invalidation immédiate des jetons JWT en circulation.

2. Diagramme de séquence Mermaid
```mermaid
sequenceDiagram
    autonumber
    actor Admin as Administrateur
    participant Front as Interface Admin (Back-office)
    participant API as Serveur API
    participant BDD as Base de Données (PostgreSQL)

    Admin ->> Front: Accéder à la liste des collaborateurs
    Admin ->> Front: Cliquer sur "Désactiver le compte" pour un employé
    Front -->> Admin: Demande de confirmation

    Admin ->> Front: Confirmer la désactivation
    Front ->> API: PATCH /api/v1/admin/employees/{id}/disable (Header: Bearer Token)

    API ->> API: VerifierRoleAdmin(token)
    API ->> BDD: ObtenirUtilisateur(id)
    BDD -->> API: Utilisateur (role='Employé', is_deleted=false)

    API ->> BDD: MettreAJourStatut(id, is_deleted=true)
    BDD -->> API: ConfirmationMaj

    API -->> Front: 200 OK ("Compte employé désactivé")
    Front -->> Admin: Actualiser affichage (Badge "Inactif / Désactivé")
```

---
=========================================================================================================
Parcours 3 : Consultation du tableau de bord décisionnel & Métriques NoSQL
=========================================================================================================

1. Règles et données métier
*   Objectifs décisionnels :
    - Visualisation du volume de commandes par catégorie et par menu.
    - Calcul du chiffre d'affaires consolidé par menu et par période (semaine, mois, année).
    - Génération de graphiques comparatifs alimentés par la structure de stockage NoSQL (MongoDB).

*   Architecture de synchronisation : Les commandes au statut `Terminée` alimentent une collection 
    semi-structurée pour soulager la base relationnelle transactionnelle (OLTP) des requêtes d'agrégation lourdes (OLAP).

2. Diagramme de séquence Mermaid
```mermaid
sequenceDiagram
    autonumber
    actor Admin as Administrateur
    participant Front as Dashboard Admin (Analytics)
    participant API as Serveur API
    participant Mongo as Base NoSQL (MongoDB)

    Admin ->> Front: Accéder au tableau de bord (période: "Mois en cours")
    Front ->> API: GET /api/v1/admin/stats?periode=mois (Header: Bearer Token)

    API ->> API: VerifierRoleAdmin(token)

    %% Agrégation NoSQL
    API ->> Mongo: AggregatePipeline(commandes_terminees, match: periode, group: menu_id)
    Note over API, Mongo: Calcul métriques : volume_commandes, total_chiffre_affaires, moyenne_panier
    Mongo -->> API: AggregationResults (données statistiques brutes)

    API ->> API: StructurerDonneesGraphiques(AggregationResults)
    API -->> Front: 200 OK (stats_menus, ca_consolide, dataset_graphiques)

    Front ->> Front: RendreGraphiques(BarChart, PieChart)
    Front -->> Admin: Afficher graphiques comparatifs et indicateurs clés (KPI)
```

---
=========================================================================================================
Parcours 4 : Modération des avis clients
=========================================================================================================

> *Ce parcours est fonctionnellement et techniquement identique au Parcours 8 de l'Employé (droits partagés).*
![Diagramme avis-client](docs/diagrammes/Diagramme-sequence_EMPLOYE_parcours8_avis-client.png ou .sva)

---
=========================================================================================================
Parcours 5 : Annulation d'une commande par le restaurant avec contact client
=========================================================================================================

> *Ce parcours est fonctionnellement et techniquement identique au Parcours 4 de l'Employé (droits partagés).*
![Diagramme Annulation-commande](DOCS/diagrammes/diagramme-de-sequence_EMPLOYE_parcour4_annulation-commande.png)
