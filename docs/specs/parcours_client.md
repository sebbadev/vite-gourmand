# Parcours Utilisateur (Client connecté) — Spécifications & Séquences

> L'acteur Client hérite des parcours publics documentés dans `parcours-visiteur.md`.

---

## Parcours 1 : Se connecter (Authentification)

### 1. Règles et données métier

* **Identifiants requis :** Email et mot de passe.
* **Mécanisme :** Vérification de l'existence du compte, comparaison sécurisée de l'empreinte (bcrypt / Argon2).
* **Gestion de session :** Génération d'un jeton d'accès sécurisé (JWT - JSON Web Token).
* **Sécurité :** Message générique en cas d'erreur (*"Identifiants invalides"*) pour empêcher l'énumération de comptes.

### 2. Diagramme de séquence Mermaid

```mermaid
sequenceDiagram
    autonumber
    actor Client as Utilisateur
    participant Front as Frontend (App/Web)
    participant API as Serveur API
    participant BDD as Base de Données

    Client ->> Front: Saisir email et mot de passe
    Client ->> Front: Cliquer sur "Se connecter"
    Note over Front: Vérification syntaxique (email valide, mot de passe non vide)
    Front ->> API: POST /api/v1/auth/login (email, password)

    API ->> BDD: ObtenirUtilisateurParEmail(email)
    BDD -->> API: Utilisateur (hash_mdp, roles, statut)

    alt Identifiants valides
        API ->> API: VerifierHashMotDePasse(password, hash_mdp)
        API ->> API: GenererTokenJWT(utilisateur_id, roles)
        API -->> Front: 200 OK (token, profil_utilisateur)
        Front ->> Front: StockerSession(token)
        Front -->> Client: Rediriger vers la page d'accueil ou commande
    else Compte inexistant ou mot de passe incorrect
        API -->> Front: 401 Unauthorized ("Identifiants invalides")
        Front -->> Client: Afficher message d'erreur générique
    end

```

---

## Parcours 2 : Réinitialiser son mot de passe

### 1. Règles et données métier

* **Sécurité anti-énumération :** Réponse HTTP 200 OK systématique côté API.
* **Jeton de réinitialisation (Reset Token) :** À usage unique, durée de vie courte (15 minutes), stocké sous forme d'empreinte hachée.

### 2. Diagramme de séquence Mermaid

```mermaid
sequenceDiagram
    autonumber
    actor Client as Utilisateur
    participant Front as Frontend (App/Web)
    participant API as Serveur API
    participant BDD as Base de Données
    participant Mail as Service Email

    rect rgb(245, 247, 250)
    Note over Client, Mail: PHASE A : Demande du lien de réinitialisation
    Client ->> Front: Saisir email et cliquer sur "Réinitialiser"
    Front ->> API: POST /api/v1/auth/forgot-password (email)
    API ->> BDD: TrouverUtilisateurParEmail(email)
    BDD -->> API: Utilisateur (trouvé ou null)

    alt Email existant en base
        API ->> API: GenererTokenSecurise(expiration=15min)
        API ->> BDD: EnregistrerResetToken(userId, hashToken, expiration)
        API ->> Mail: EnvoyerLienReinitialisation(email, token)
        Mail -->> API: EmailEnvoye
    else Email inexistant
        Note over API: Ne rien faire (protection contre l'énumération)
    end

    API -->> Front: 200 OK ("Si le compte existe, un email a été envoyé")
    Front -->> Client: Afficher message de confirmation
    end

    rect rgb(240, 249, 255)
    Note over Client, Mail: PHASE B : Validation du nouveau mot de passe
    Client ->> Front: Cliquer sur le lien dans l'email (/reset-password?token=xyz)
    Front -->> Client: Afficher formulaire de nouveau mot de passe

    Client ->> Front: Saisir nouveau mot de passe et confirmer
    Note over Front: Vérification de correspondance et robustesse
    Front ->> API: POST /api/v1/auth/reset-password (token, nouveauPassword)

    API ->> BDD: ObtenirToken(hashToken)
    BDD -->> API: DonneesToken (userId, expiration, estUtilise)

    alt Token valide et non expiré
        API ->> API: HasherMotDePasse(nouveauPassword)
        API ->> BDD: MajMotDePasse(userId, nouveauHash)
        API ->> BDD: InvaliderToken(hashToken)
        API -->> Front: 200 OK ("Mot de passe mis à jour avec succès")
        Front -->> Client: Rediriger vers la page de connexion
    else Token invalide ou expiré
        API -->> Front: 400 Bad Request ("Lien expiré ou invalide")
        Front -->> Client: Afficher message d'erreur et proposer une nouvelle demande
    end
    end

```

---

## Parcours 3 : Passer commande et régler sa commande

### 1. Règles et données métier

* **Gestion découplée des 3 statuts :** `statut_commande`, `statut_paiement`, `statut_materiel`.
* **Clôture finale (`TERMINÉE`) conditionnelle :** Uniquement si `LIVRÉE` + `RÉGLÉE` + `RETOURNÉ` (ou matériel non inclus).

### 2. Diagramme de séquence Mermaid

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant Front as Frontend Web/App
    participant API as Serveur API
    participant BDD as Base de Données
    actor Resto as Équipe Resto / Admin
    actor Livreur
    participant Mail as Service Notif / Email
    participant Banque as Passerelle Paiement

    rect rgb(245, 247, 250)
    Note over Client, BDD: 1. Demande de commande (sans paiement direct)
    Client ->> Front: Valider la commande (panier, date, adresse)
    Front ->> API: POST /api/v1/commandes (panier, date_livraison, adresse)

    API ->> BDD: VerifierDispoEtEligibilite(date, menus, materiel, client_id)
    BDD -->> API: EtatDisponibilites

    API ->> BDD: InsererCommande(statut_cmd: "EN_ATTENTE_VALIDATION", statut_paie: "EN_ATTENTE", statut_mat: "INCLUS")
    BDD -->> API: CommandeCreee(id_commande)

    API ->> Mail: EnvoyerAccuseReception(client_email, id_commande)
    API -->> Front: 201 Created (id_commande, statut: "EN_ATTENTE_VALIDATION")
    Front -->> Client: Afficher "Commande en cours de validation par le restaurant"
    end

    rect rgb(254, 249, 235)
    Note over Resto, API: 2. Validation par l'équipe du restaurant
    API ->> Resto: NotifierNouvelleCommande(id_commande, recap_dispos)

    alt Restaurateur REFUSE la commande
        Resto ->> API: POST /api/v1/commandes/{id}/refuser (motif)
        API ->> BDD: MajStatuts(statut_cmd: "ANNULEE")
        API ->> Mail: NotifierRefusClient(client_email, motif)
        API -->> Resto: 200 OK
    else Restaurateur ACCEPTE la commande
        Resto ->> API: POST /api/v1/commandes/{id}/accepter
        API ->> BDD: MajStatuts(statut_cmd: "ACCEPTEE")
        API ->> Banque: GenererLienPaiementUnique(id_commande, montant)
        Banque -->> API: url_paiement
        API ->> Mail: EnvoyerConfirmationEtLienPaiement(client_email, url_paiement)
        API -->> Resto: 200 OK
    end
    end

    rect rgb(240, 249, 255)
    Note over Resto, Livreur: 3. Préparation et acheminement
    Resto ->> API: PUT /api/v1/commandes/{id}/statut (statut_cmd: "EN_PREPARATION")
    Resto ->> API: PUT /api/v1/commandes/{id}/statut (statut_cmd: "EN_LIVRAISON")
    
    API ->> Livreur: AssignerLivraison(id_commande, adresse)
    Livreur ->> Resto: RecupererCommandeEtMateriel()

    Livreur ->> Client: Remettre repas + matériel
    Livreur ->> API: POST /api/v1/commandes/{id}/confirmer-livraison
    API ->> BDD: MajStatuts(statut_cmd: "LIVREE", statut_mat: "INCLUS")
    API ->> Mail: NotifierLivraisonEffectueeEtRappelMateriel(client_email, delai: "10 jours", penalite: "600€")
    end

    rect rgb(245, 255, 245)
    Note over Client, Banque: 4. Règlement de la commande
    alt Paiement sur place avec le livreur
        Client ->> Livreur: Régler par TPE / Espèces
        Livreur ->> API: POST /api/v1/commandes/{id}/encaisser (mode: "SUR_PLACE")
        API ->> BDD: MajStatutPaiement("REGLEE")
    else Paiement en ligne via le lien
        Client ->> Banque: Ouvrir lien et payer par CB
        Banque ->> API: POST /api/v1/webhooks/paiement (event: payment_intent.succeeded)
        API ->> BDD: MajStatutPaiement("REGLEE")
    end
    end

    rect rgb(255, 245, 245)
    Note over Client, BDD: 5. Restitution du matériel sous 10 jours
    alt Cas nominal : Matériel restitué dans les délais (<= 10 jours)
        Client ->> Resto: Restituer le matériel emprunté
        Resto ->> API: POST /api/v1/commandes/{id}/restitution-materiel (etat: "CONFORME")
        API ->> BDD: MajStatutMateriel("RETOURNE")

        API ->> BDD: VerifierEligibiliteCloture(id_commande)
        Note over API, BDD: Condition : statut_cmd="LIVREE" ET statut_paie="REGLEE" ET statut_mat="RETOURNE"
        API ->> BDD: MajStatutCommande("TERMINÉE")
        API ->> Mail: EnvoyerRecuEtClotureDossier(client_email)
    else Cas pénalité : Dépassement > 10 jours ou non restitué
        Note over API, BDD: Détection automatique d'échéance ou constat employé
        Resto ->> API: POST /api/v1/commandes/{id}/litige-materiel (motif: "Non restitution sous 10 jours")
        API ->> BDD: MajStatutMateriel("NON_INCLUS")
        API ->> BDD: CreerFacturePenalite(id, montant: 600)
        API ->> Mail: EnvoyerNotificationPenalite(client_email, id, montant: "600€")
    end
    end

```

---

## Parcours 4 : Suivre l'état de sa commande

### 1. Règles et données métier

* **Contrôle d'accès :** Accès strictement réservé au propriétaire de la commande (`user_id`).
* **Visualisation :** Frise chronologique horodatée permettant de suivre l'avancement de la préparation, de la livraison et du statut du matériel.

### 2. Diagramme de séquence Mermaid

```mermaid
sequenceDiagram
    autonumber
    actor Client as Utilisateur
    participant Front as Frontend (App/Web)
    participant API as Serveur API
    participant BDD as Base de Données

    Client ->> Front: Accéder à la page "Suivi de commande" (/commandes/{id})
    Front ->> API: GET /api/v1/commandes/{id} (Headers: Authorization Bearer Token)

    API ->> BDD: ObtenirCommandeEtStatuts(id)
    BDD -->> API: Commande (userId, statut, statut_paiement, statut_materiel, date_livraison, items)

    alt Utilisateur non propriétaire de la commande
        API -->> Front: 403 Forbidden ("Accès refusé")
        Front -->> Client: Afficher message d'erreur et redirection
    else Utilisateur autorisé
        API ->> BDD: ObtenirHistoriqueEtDelaisMateriel(id)
        BDD -->> API: HistoriqueEtDelais (timeline, date_prestation)

        API -->> Front: 200 OK (details_commande, statuts, lien_paiement)
        
        Front ->> Front: ConstruireVueSuivi(timeline, statuts)
        Front -->> Client: Afficher frise chronologique & état des 3 statuts

        opt Commande livrée avec matériel à restituer
            Note over Front, Client: Alerte visuelle : "Matériel à restituer avant le [Date livraison + 10 jours]"
        end

        opt Paiement toujours en attente
            Note over Front, Client: Bouton d'action actif : "Payer ma commande en ligne"
        end
    end

```

---

## Parcours 5 : Restituer son matériel emprunté

### 1. Règles et données métier

* **Délai maximal :** 10 jours ouvrés / calendaires.
* **Notification de rappel de paiement :** Si le matériel est restitué mais que le règlement n'est pas soldé, un email de rappel de paiement dû est envoyé au client.
* **Pénalité forfaitaire :** 600 € appliqués si le matériel est non restitué ou détérioré.

### 2. Diagramme de séquence Mermaid

```mermaid
sequenceDiagram
    autonumber
    actor Client as Utilisateur
    actor Resto as Restaurateur / Employé
    participant FrontResto as Interface Resto (Back-office)
    participant API as Serveur API
    participant BDD as Base de Données
    participant Mail as Service Email

    Client ->> Resto: Déposer le matériel emprunté (avec réf commande)
    Resto ->> Resto: Inspecter l'état du matériel (complet, propre, non cassé)

    Resto ->> FrontResto: Saisir réf commande et résultat contrôle
    FrontResto ->> API: POST /api/v1/commandes/{id}/restitution (statut_retour: "CONFORME")

    API ->> BDD: ObtenirCommandePourRestitution(id)
    BDD -->> API: Commande (statut_paiement, heure_livraison)

    API ->> API: VerifierDelai(date_actuelle <= date_livraison + 10 jours)

    alt Matériel restitué à temps (<= 10 jours) et conforme
        API ->> BDD: MajStatutMateriel(id, "RETOURNE")
        
        alt Paiement déjà soldé
            API ->> BDD: MajStatutCommande(id, "TERMINÉE")
            Note over API, BDD: Commande 100% soldée et archivée
        else Paiement encore en attente
            API ->> Mail: EnvoyerRappelPaiementDu(client_email, id)
            Note over API: Commande reste à "LIVRÉE" jusqu'au paiement
        end

        API ->> Mail: EnvoyerAccuseRestitutionConforme(client_email, id)
        API -->> FrontResto: 200 OK ("Restitution validée avec succès")
        FrontResto -->> Resto: Afficher confirmation écran

    else Dépassement de délai (> 10 jours) ou matériel dégradé
        API ->> BDD: MajStatutMateriel(id, "NON_INCLUS")
        API ->> BDD: CreerFacturePenalite(id, montant: 600)
        API ->> Mail: EnvoyerNotificationPenalite(client_email, id, montant: "600€")
        API -->> FrontResto: 200 OK ("Dossier basculé en litige / pénalité")
        FrontResto -->> Resto: Alerte "Dossier pénalité généré"
    end

```

---

## Parcours 6 : Voir l'historique des commandes

### 1. Règles et données métier

* **Pagination côté serveur :** Paramètres `limit` et `page` requis.
* **Émission de facture PDF :** Accessible dès que la commande passe au statut `LIVRÉE` (avec mention légale *"À RÉGLER"* ou *"ACQUITTÉE"*).
* **Annulation autonome par le client :** Autorisée uniquement tant que le statut de la commande est `En attente de validation`.

### 2. Diagramme de séquence Mermaid

```mermaid
sequenceDiagram
    autonumber
    actor Client as Utilisateur
    participant Front as Frontend (App/Web)
    participant API as Serveur API
    participant BDD as Base de Données
    participant Storage as Service Factures / PDF
    participant Mail as Service Email

    %% 1. Consultation paginée de l'historique
    Client ->> Front: Accéder à "Mes commandes"
    Front ->> API: GET /api/v1/commandes?page=1&limit=10 (Header: Bearer Token)

    API ->> API: ExtraireUserIdDepuisToken()
    API ->> BDD: ObtenirCommandesClient(userId, page=1, limit=10)
    BDD -->> API: ListeCommandes (id, date, montant, statuts, heure_livraison) + TotalCount

    API -->> Front: 200 OK (commandes, pagination)
    Front ->> Front: GenererVueHistorique(commandes)
    Front -->> Client: Afficher liste des commandes avec statuts et actions

    %% 2. Téléchargement de la facture (Dès livraison)
    opt Télécharger une facture
        Client ->> Front: Cliquer sur "Télécharger facture (PDF)"
        Front ->> API: GET /api/v1/commandes/{id}/facture (Header: Bearer Token)

        API ->> BDD: VerifierStatutCommande(id, userId)
        BDD -->> API: Commande (statut, statut_paiement, prix_total, client_data)

        alt Commande déjà livrée (statut in ["LIVRÉE", "TERMINÉE"])
            alt Commande non payée (statut_paiement = "EN_ATTENTE_DE_RÈGLEMENT")
                API ->> Storage: GenererFacturePDF(id, mention: "À RÉGLER", date_echeance)
            else Commande déjà réglée (statut_paiement = "RÉGLÉE")
                API ->> Storage: GenererFacturePDF(id, mention: "ACQUITTÉE", date_reglement)
            end

            Storage -->> API: FluxFichierPDF (buffer / url)
            API -->> Front: 200 OK (application/pdf, facture_{id}.pdf)
            Front -->> Client: Déclencher téléchargement du document PDF

        else Commande non encore livrée (statut < "LIVRÉE")
            API -->> Front: 400 Bad Request ("Facture disponible dès la livraison effective")
            Front -->> Client: Notification "Votre facture sera générée à la livraison"
        end
    end

    %% 3. Annulation autonome par le client (avant acceptation)
    opt Annuler une commande en attente
        Client ->> Front: Cliquer sur "Annuler ma commande" (sur commande en attente)
        Front ->> API: POST /api/v1/commandes/{id}/annuler (Header: Bearer Token)

        API ->> BDD: VerifierStatutCommande(id, userId)
        BDD -->> API: Commande (statut, menu_id, quantite)

        alt Commande toujours en attente
            API ->> BDD: MajStatutCommande(id, statut="Annulée", motif="Annulation par le client", updated_at=now())
            API ->> BDD: ReincrementerStockMenu(menu_id, quantite)
            BDD -->> API: ConfirmationMaj

            API ->> Mail: EnvoyerConfirmationAnnulation(client_email, id)
            API -->> Front: 200 OK ("Commande annulée avec succès")
            Front -->> Client: Actualiser badge statut ("Annulée") et libérer le créneau
        else Commande déjà acceptée entre-temps
            API -->> Front: 400 Bad Request ("Impossible d'annuler : commande déjà acceptée")
            Front -->> Client: Alerte ("Veuillez contacter le restaurant pour toute annulation")
        end
    end

```

---

## Parcours 7 : Modifier les informations de son compte

### 1. Règles et données métier

* **Authentification requise :** Header `Authorization: Bearer <Token>`.
* **Cas A :** Coordonnées personnelles (nom, prénom, téléphone, adresse).
* **Cas B :** Sécurité (changement de mot de passe avec validation préalable de l'ancien mot de passe).

### 2. Diagramme de séquence Mermaid

```mermaid
sequenceDiagram
    autonumber
    actor Client as Utilisateur
    participant Front as Frontend (App/Web)
    participant API as Serveur API
    participant BDD as Base de Données
    participant Mail as Service Email

    %% 1. Chargement initial
    Client ->> Front: Accéder à "Mon profil"
    Front ->> API: GET /api/v1/users/me (Header: Bearer Token)
    API ->> BDD: ObtenirProfil(userId)
    BDD -->> API: ProfilUtilisateur (nom, prenom, email, telephone, adresse)
    API -->> Front: 200 OK (données profil)
    Front -->> Client: Afficher formulaire pré-rempli

    %% 2. Cas A : Modification coordonnées
    alt Cas A : Modification des coordonnées générales
        Client ->> Front: Modifier nom, prenom, telephone, adresse et valider
        Front ->> API: PATCH /api/v1/users/me (payload: coordonnées)
        API ->> API: ValiderDonnees()
        API ->> BDD: MettreAJourCoordonnees(userId, payload)
        BDD -->> API: ProfilMisAJour
        API -->> Front: 200 OK (profil actualisé)
        Front -->> Client: Afficher confirmation ("Coordonnées mises à jour")

    %% 3. Cas B : Modification du mot de passe
    else Cas B : Modification du mot de passe
        Client ->> Front: Saisir ancien mot de passe, nouveau mot de passe et confirmer
        Note over Front: Vérification robustesse et correspondance
        Front ->> API: PATCH /api/v1/users/me/password (ancien_mdp, nouveau_mdp)
        API ->> BDD: ObtenirHashMotDePasse(userId)
        BDD -->> API: hash_actuel

        alt Ancien mot de passe valide
            API ->> API: VerifierHash(ancien_mdp, hash_actuel)
            API ->> API: HasherNouveauMotDePasse(nouveau_mdp)
            API ->> BDD: MettreAJourHash(userId, nouveau_hash)
            API ->> Mail: EnvoyerAlerteSecurite(email, "Mot de passe modifié")
            Mail -->> API: EmailEnvoye
            API -->> Front: 200 OK ("Mot de passe mis à jour")
            Front -->> Client: Afficher confirmation de sécurité
        else Ancien mot de passe erroné
            API -->> Front: 400 Bad Request ("Le mot de passe actuel est incorrect")
            Front -->> Client: Afficher message d'erreur
        end
    end

```

---

## Parcours 8 : Déposer un avis suite à une commande terminée

### 1. Règles et données métier

* **Condition d'accès :** La commande doit obligatoirement être au statut `Terminée` (`OrderStatus.TERMINEE`).
* **Architecture polyglotte :** Le contrôle d'éligibilité s'effectue sur la base relationnelle (PostgreSQL), tandis que la persistance de l'avis s'effectue dans une collection NoSQL (MongoDB).
* **Évaluation multicritère :** Notes sur la qualité, le service, le prix (1 à 5 / type enum `Rating`), complétées par un commentaire descriptif.
* **Statut initial :** L'avis est inséré avec le statut `En attente` (`ReviewStatus.EN_ATTENTE`), invisible sur la vitrine publique tant qu'il n'est pas validé par un employé ou l'administrateur.

### 2. Diagramme de séquence Mermaid

```mermaid
sequenceDiagram
    autonumber
    actor Client as Client Connecté
    participant Front as Frontend (App/Web)
    participant API as Serveur API
    participant BDD as BDD Relationnelle (PostgreSQL)
    participant Mongo as BDD NoSQL (MongoDB)

    Client ->> Front: Accéder à la commande terminée (via notification ou espace client)
    Client ->> Front: Cliquer sur "Donner mon avis"
    Front -->> Client: Afficher formulaire d'avis (notes: qualité, service, prix + commentaire)

    Client ->> Front: Saisir les notes, rédiger le commentaire et valider
    Front ->> API: POST /api/v1/commandes/{id}/avis (qualite, service, prix, description) (Header: Bearer Token)

    %% 1. Contrôle métier dans PostgreSQL (intégrité de la commande)
    API ->> BDD: VerifierProprietaireEtCommandeTerminee(id, userId)
    BDD -->> API: CommandeValide (menu_id, client_id)

    %% 2. Contrôle d'unicité et insertion dans MongoDB
    API ->> Mongo: findOne({ commande_id: id, user_id: userId })
    Mongo -->> API: null (aucun avis préalable)

    API ->> Mongo: insertOne({ commande_id: id, user_id: userId, menu_id: menu_id, notes: { qualite, service, prix }, description: text, statut: "En attente", created_at: ISODate() })
    Mongo -->> API: Acknowledged (insertedId)

    API -->> Front: 201 Created ("Avis soumis pour modération")
    Front -->> Client: Notification succès ("Merci ! Votre avis sera publié après validation.")

```
