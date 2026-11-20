# Parcours Collaborateur (Employé) — Spécifications & Séquences

> Cet acteur hérite des parcours publics documentés dans `parcours-visiteur.md` et `parcours-client.md` :
> - Visiter la boutique, filtrer, consulter le détail
> - Se connecter (Authentification)
> - Réinitialiser son mot de passe
> - Prendre contact
> - Modifier les informations de son compte

---

## Parcours 1 : Validation d'une commande client (Acceptation / Refus)

### 1. Règles et données métier

* **Point d'entrée :** Commandes arrivant avec le statut `En attente de validation` (`OrderStatus.EN_ATTENTE_DE_VALIDATION`).
* **Contrôle préalable :** L'employé vérifie la faisabilité opérationnelle en cuisine et les stocks disponibles.
* **Décision :**
  * **Acceptée** (`OrderStatus.ACCEPTEE`) : Déclenche la génération du lien de paiement sécurisé et l'envoi d'un email de confirmation au client.
  * **Refusée / Annulée** (`OrderStatus.ANNULEE`) : Saisie obligatoire du motif de refus, notification email au client et réincrémentation des stocks (`quantite_disponible`).

### 2. Diagramme de séquence Mermaid

```mermaid
sequenceDiagram
    autonumber
    actor Employe as Collaborateur (Employé)
    participant Front as Interface Back-office
    participant API as Serveur API
    participant BDD as Base de Données (PostgreSQL)
    participant Mail as Service Email
    participant Banque as Passerelle Paiement

    Employe ->> Front: Consulter les commandes en attente
    Front ->> API: GET /api/v1/admin/commandes?statut=En attente de validation (Header: Bearer Token)
    API ->> API: VerifierRoleEmployeOuAdmin(token)
    API ->> BDD: ObtenirCommandesEnAttente()
    BDD -->> API: ListeCommandes (id, date_prestation, menus, prix_total, client)
    API -->> Front: 200 OK (commandes)
    Front -->> Employe: Afficher liste avec actions [Accepter] / [Refuser]

    alt Décision : Accepter la commande
        Employe ->> Front: Cliquer sur "Accepter"
        Front ->> API: POST /api/v1/admin/commandes/{id}/accepter (Header: Bearer Token)
        API ->> BDD: MajStatutCommande(id, statut='Acceptée')
        API ->> Banque: GenererLienPaiement(id, montant)
        Banque -->> API: url_paiement
        API ->> Mail: EnvoyerConfirmationEtLienPaiement(client_email, url_paiement)
        Mail -->> API: EmailEnvoye
        API -->> Front: 200 OK ("Commande acceptée")
        Front -->> Employe: Statut mis à jour : "Acceptée"
    else Décision : Refuser la commande
        Employe ->> Front: Cliquer sur "Refuser" et renseigner le motif
        Front ->> API: POST /api/v1/admin/commandes/{id}/refuser (motif)
        API ->> BDD: MajStatutCommande(id, statut='Annulée', motif_annulation=motif)
        API ->> BDD: ReincrementerStockMenu(menu_id, quantite)
        API ->> Mail: EnvoyerNotificationRefus(client_email, motif)
        Mail -->> API: EmailEnvoye
        API -->> Front: 200 OK ("Commande refusée et stock libéré")
        Front -->> Employe: Statut mis à jour : "Annulée"
    end

```

---

## Parcours 2 : Suivi et mise à jour des statuts de préparation et livraison

### 1. Règles et données métier

* **Transitions ordonnées :** `Acceptée` $\rightarrow$ `En préparation` $\rightarrow$ `En cours de livraison` $\rightarrow$ `Livrée`.
* **Historisation :** Mise à jour automatique de la colonne technique d'audit `updated_at`.
* **Règles d'accès :** Réservé aux utilisateurs disposant du rôle `Employé` ou `Administrateur`.

### 2. Diagramme de séquence Mermaid

```mermaid
sequenceDiagram
    autonumber
    actor Employe as Collaborateur (Employé)
    participant Front as Interface Back-office
    participant API as Serveur API
    participant BDD as Base de Données (PostgreSQL)

    Employe ->> Front: Accéder au tableau des commandes du jour
    Front ->> API: GET /api/v1/admin/commandes/actives (Header: Bearer Token)
    API ->> BDD: ObtenirCommandesActives()
    BDD -->> API: ListeCommandes (id, statut, heure_livraison)
    API -->> Front: 200 OK (liste)
    Front -->> Employe: Afficher tableau de bord opérationnel

    Employe ->> Front: Mettre à jour le statut (ex: passer à "En préparation")
    Front ->> API: PATCH /api/v1/admin/commandes/{id}/statut (nouveau_statut: "En préparation")
    API ->> API: VerifierTransitionValide(ancien_statut, nouveau_statut)
    API ->> BDD: MajStatutCommande(id, statut="En préparation", updated_at=now())
    BDD -->> API: ConfirmationMaj
    API -->> Front: 200 OK (commande_mise_a_jour)
    Front -->> Employe: Actualiser badge statut ("En préparation")

```

---

## Parcours 3 : Consultation de l'historique et recherche multicritère

### 1. Règles et données métier

* **Filtres multicritères :** Recherche par identifiant/nom de client, statut de commande, statut de paiement, ou plage de dates de prestation.
* **Pagination :** Implémentation de la pagination serveur (`page`, `limit`) pour préserver les performances de la base de données.

### 2. Diagramme de séquence Mermaid

```mermaid
sequenceDiagram
    autonumber
    actor Employe as Collaborateur (Employé)
    participant Front as Interface Back-office
    participant API as Serveur API
    participant BDD as Base de Données (PostgreSQL)

    Employe ->> Front: Ouvrir la vue "Historique des commandes"
    Employe ->> Front: Saisir filtres (client="Dupont", statut="Terminée", date="2026-11")
    Front ->> API: GET /api/v1/admin/commandes?client=Dupont&statut=Terminée&page=1&limit=20
    API ->> API: VerifierRoleEmployeOuAdmin(token)
    API ->> BDD: ExecuterRequeteFiltree(criteres, offset, limit)
    BDD -->> API: Resultats (commandes, pagination_metadata)
    API -->> Front: 200 OK (données_historique)
    Front -->> Employe: Afficher le tableau de résultats paginé

```

---

## Parcours 4 : Annulation d'une commande acceptée avec contact client obligatoire

### 1. Règles et données métier

* **Règle métier stricte (Cahier des charges) :** Interdiction d'annuler une commande acceptée sans avoir préalablement contacté le client (par téléphone ou email).
* **Traçabilité requise :** Saisie obligatoire de `motif_annulation` (texte), sélection de `mode_contact_annulation` (`Téléphone` ou `Email`), et attestation `contact_client_effectue = true`.
* **Rétablissement des stocks :** Restitution automatique des quantités réservées dans la table `menus`.

### 2. Diagramme de séquence Mermaid

```mermaid
sequenceDiagram
    autonumber
    actor Employe as Collaborateur (Employé)
    participant Front as Interface Back-office
    participant API as Serveur API
    participant BDD as Base de Données (PostgreSQL)
    participant Mail as Service Email

    Employe ->> Front: Sélectionner la commande acceptée à annuler
    Employe ->> Front: Cliquer sur "Annuler la commande"
    Front -->> Employe: Boîte de dialogue : Motif requis + modalité de contact client

    Employe ->> Front: Saisir le motif, sélectionner le mode de contact (GSM/Email) et cocher "Client contacté"
    Front ->> API: POST /api/v1/admin/commandes/{id}/annuler (motif, mode_contact, contact_client_effectue=true)

    API ->> API: VerifierChampsAudit(motif, mode_contact, contact_client_effectue)
    API ->> BDD: ObtenirDetailCommande(id)
    BDD -->> API: Commande (id, menu_id, quantite, client_email)

    API ->> BDD: MajAnnulationCommande(id, statut='Annulée', motif, mode_contact, contact_client_effectue=true)
    API ->> BDD: ReincrementerStockMenu(menu_id, quantite)
    BDD -->> API: ConfirmationMaj

    API ->> Mail: EnvoyerAvisAnnulationClient(client_email, motif)
    Mail -->> API: EmailEnvoye

    API -->> Front: 200 OK ("Commande annulée, stock libéré et client notifié")
    Front -->> Employe: Afficher badge "Annulée"

```

---

## Parcours 5 : Livraison de la commande et encaissement sur place

### 1. Règles et données métier

* **Double action :** Remise de la marchandise et du matériel consigné, puis régularisation du règlement si non payé en ligne.
* **Mise à jour des statuts :**
* `statut` passe à `'Livrée'` (`OrderStatus.LIVREE`).
* `statut_paiement` passe à `'Réglée'` (`PaymentStatus.REGLEE`).
* `statut_materiel` passe à `'Inclus'` (`Equipment.INCLUS`).


* **Activation du délai de restitution :** Déclenchement du délai de 10 jours ouvrés pour la restitution du matériel, sous peine de 600 € d'indemnité forfaitaire mentionnée aux CGV.

### 2. Diagramme de séquence Mermaid

```mermaid
sequenceDiagram
    autonumber
    actor Employe as Collaborateur (Livreur / Employé)
    actor Client as Client Destinataire
    participant FrontMobile as App Mobile / Terminal
    participant API as Serveur API
    participant BDD as Base de Données (PostgreSQL)
    participant Mail as Service Email

    Employe ->> Client: Remettre repas et équipement (chafing dish / vaisselle)
    alt Paiement déjà réglé en ligne
        Note over Employe, Client: Aucun encaissement requis
    else Règlement sur place
        Client ->> Employe: Régler par TPE mobile / Espèces
        Employe ->> FrontMobile: Saisir encaissement ("Réglée")
    end

    Employe ->> FrontMobile: Valider la livraison
    FrontMobile ->> API: POST /api/v1/admin/commandes/{id}/livrer (paiement_effectue=true)
    
    API ->> BDD: MajStatutsLivraison(id, statut='Livrée', statut_paiement='Réglée', statut_materiel='Inclus')
    BDD -->> API: ConfirmationMaj

    API ->> Mail: NotifierLivraisonEtRappelRestitution(client_email, delai: "10 jours", penalite: "600€")
    Mail -->> API: EmailEnvoye

    API -->> FrontMobile: 200 OK ("Livraison validée")
    FrontMobile -->> Employe: Écran de confirmation de livraison

```

---

## Parcours 6 : Réception et contrôle de conformité du matériel retourné

### 1. Règles et données métier

* **Délai contractuel :** 10 jours ouvrés / calendaires maximum après la livraison.
* **Contrôle qualitatif :**
* **Cas conforme :** `statut_materiel` passe à `'Retourné'` (`Equipment.RETOURNE`).
* **Cas clôture :** Si `statut == 'Livrée'` ET `statut_paiement == 'Réglée'` ET `statut_materiel == 'Retourné'`, alors `statut` bascule automatiquement à `'Terminée'` (`OrderStatus.TERMINEE`).
* **Cas non conforme / Dépassé :** Notification d'anomalie et basculement en litige avec facturation de l'indemnité forfaitaire (600 €).



### 2. Diagramme de séquence Mermaid

```mermaid
sequenceDiagram
    autonumber
    actor Client as Client Déposant
    actor Employe as Collaborateur (Employé)
    participant Front as Interface Back-office
    participant API as Serveur API
    participant BDD as Base de Données (PostgreSQL)
    participant Mongo as Base NoSQL (MongoDB)
    participant Mail as Service Email

    Client ->> Employe: Déposer le matériel prêté (référence commande)
    Employe ->> Employe: Contrôler l'état physique (complet, propre, non détérioré)
    Employe ->> Front: Saisir référence commande et ouvrir écran restitution
    Front ->> API: GET /api/v1/admin/commandes/{id}
    API ->> BDD: ObtenirCommande(id)
    BDD -->> API: Commande (date_prestation, statut, statut_paiement)
    API -->> Front: 200 OK (details)

    alt Matériel complet et rendu sous 10 jours
        Employe ->> Front: Valider retour "Conforme"
        Front ->> API: POST /api/v1/admin/commandes/{id}/restitution (statut_materiel='Retourné')
        API ->> BDD: MajStatutMateriel(id, 'Retourné')
        
        %% Évaluation de la clôture complète
        opt Commande livrée et totalement réglée
            API ->> BDD: MajStatutCommande(id, statut='Terminée')
            Note over API, BDD: Commande soldée dans PostgreSQL
            
            %% SYNCHRONISATION ANALYTIQUE VERS MONGODB
            API ->> Mongo: insertOne(document_commande_terminee)
            Note over API, Mongo: Synchronisation dénormalisée pour stats Admin
            Mongo -->> API: Acknowledged (insertedId)
        end

        API ->> Mail: EnvoyerAccuseRestitutionConforme(client_email)
        Mail -->> API: EmailEnvoye
        API -->> Front: 200 OK ("Restitution validée, dossier clôturé")
        Front -->> Employe: Confirmation écran ("Matériel restitué")
    else Dépassement > 10 jours ou matériel cassé / manquant
        Employe ->> Front: Signaler litige / non-restitution
        Front ->> API: POST /api/v1/admin/commandes/{id}/litige-materiel (motif)
        API ->> BDD: MajStatutMateriel(id, 'Non inclus')
        API ->> Mail: EnvoyerAlertePenalite(client_email, montant: "600€")
        Mail -->> API: EmailEnvoye
        API -->> Front: 200 OK ("Dossier basculé en litige")
        Front -->> Employe: Alerte litige enregistrée
    end

```

---

## Parcours 7 : Gestion opérationnelle du catalogue (Menus, Plats, Horaires)

### 1. Règles et données métier

* **Prérogatives opérationnelles de l'employé :** Création, modification et suppression logique (`is_deleted = true`, `is_active = false`) des menus, plats, régimes, allergènes et horaires d'ouverture.
* **Règles d'intégrité :** Un menu doit contenir au minimum un plat, un titre, un prix par personne, une quantité disponible et un nombre minimal de personnes.

### 2. Diagramme de séquence Mermaid

```mermaid
sequenceDiagram
    autonumber
    actor Employe as Collaborateur (Employé)
    participant Front as Interface Back-office
    participant API as Serveur API
    participant BDD as Base de Données (PostgreSQL)

    Employe ->> Front: Accéder à la gestion du catalogue
    Employe ->> Front: Renseigner nouveau menu (titre, prix, min_personnes, plats_associes)
    Employe ->> Front: Cliquer sur "Enregistrer le menu"

    Front ->> API: POST /api/v1/admin/menus (payload_menu) (Header: Bearer Token)
    API ->> API: VerifierRoleEmployeOuAdmin(token)
    API ->> API: ValiderIntegrite(min_plats >= 1, prix > 0)

    API ->> BDD: InsererMenu(titre, prix_par_personne, min_personnes, quantite)
    BDD -->> API: MenuCree(menu_id)

    API ->> BDD: AssocierPlatsEtThemes(menu_id, plat_ids, theme_ids)
    BDD -->> API: AssociationConfirmee

    API -->> Front: 201 Created (menu_id, resume_menu)
    Front -->> Employe: Notification succès ("Menu ajouté au catalogue")

```

---

## Parcours 8 : Modération et validation des avis clients (Collection NoSQL)

### 1. Règles et données métier

* **Cycle de publication :** L'employé filtre les avis stockés dans la collection MongoDB `avis` au statut initial `En attente` (`ReviewStatus.EN_ATTENTE`).
* **Contrôle :** Validation (`Approuvé` / publication vitrine) ou rejet (`Rejeté` / archivage non visible).
* **Stockage NoSQL :** La mise à jour du statut s'opère directement sur le document MongoDB sans impacter PostgreSQL.

### 2. Diagramme de séquence Mermaid

```mermaid
sequenceDiagram
    autonumber
    actor Employe as Collaborateur (Employé)
    participant Front as Interface Back-office
    participant API as Serveur API
    participant Mongo as BDD NoSQL (MongoDB)

    Employe ->> Front: Accéder à l'écran "Modération des avis"
    Front ->> API: GET /api/v1/admin/avis?statut=En attente (Header: Bearer Token)
    API ->> API: VerifierRoleEmployeOuAdmin(token)

    %% Lecture dans MongoDB
    API ->> Mongo: find({ statut: "En attente" }).sort({ created_at: -1 })
    Mongo -->> API: ListeDocumentsAvis (id, user_id, menu_id, notes, description)

    API -->> Front: 200 OK (liste_avis)
    Front -->> Employe: Présenter liste des avis à modérer

    alt Validation de l'avis pour publication
        Employe ->> Front: Cliquer sur "Valider pour publication"
        Front ->> API: PATCH /api/v1/admin/avis/{id} (statut: "Approuvé")
        API ->> Mongo: updateOne({ _id: id }, { $set: { statut: "Approuvé", updated_at: ISODate() } })
        Mongo -->> API: Acknowledged (modifiedCount: 1)
        API -->> Front: 200 OK
        Front -->> Employe: Avis publié sur la vitrine publique

    else Rejet de l'avis
        Employe ->> Front: Cliquer sur "Rejeter"
        Front ->> API: PATCH /api/v1/admin/avis/{id} (statut: "Rejeté")
        API ->> Mongo: updateOne({ _id: id }, { $set: { statut: "Rejeté", updated_at: ISODate() } })
        Mongo -->> API: Acknowledged (modifiedCount: 1)
        API -->> Front: 200 OK
        Front -->> Employe: Avis archivé en statut rejeté
    end

```