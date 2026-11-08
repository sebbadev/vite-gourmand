# Parcours Visiteur — Spécifications & Séquences

> Ce document détaille les parcours publics ouverts aux utilisateurs non authentifiés (visiteurs).

---

## Parcours 1 : Visiter la boutique, filtrer, consulter le détail et commander

### 1. Règles et données métier

* **Structure d'un Menu :** Un ou plusieurs plats, nombre minimal de personnes, prix unitaire par personne, description, quantité disponible, liste d'allergènes, régimes alimentaires compatibles et thèmes associés.
* **Filtres gérés côté client (mémoire locale) :** Nombre de personnes, budget/prix maximum, exclusion d'allergènes, régimes alimentaires, thèmes.
* **Navigation après clic « Commander » :**
  * Si l'utilisateur possède déjà une session active (jeton JWT valide) : redirection vers l'écran de création d'une nouvelle commande (`/commande/nouvelle?menu_id={id}`).
  * Sinon : redirection vers la mire de connexion (`/connexion?redirect=/commande/nouvelle?menu_id={id}`).

### 2. Diagramme de séquence Mermaid

```mermaid
sequenceDiagram
    autonumber
    actor Visiteur
    participant Front as Frontend (App/Web)
    participant Auth as Gestionnaire Session
    participant API as Serveur API
    participant BDD as Base de Données (PostgreSQL)

    %% 1. Chargement initial
    Visiteur ->> Front: Accéder à la boutique
    Front ->> API: GET /api/v1/menus
    API ->> BDD: ObtenirMenusAvecMetadata()
    BDD -->> API: Menus (id, titre, prix_par_personne, min_pers, regimes, themes, allergenes)
    API -->> Front: 200 OK (liste_menus)
    Front ->> Front: StockerEnMemoire(liste_menus)
    Front -->> Visiteur: Afficher catalogue

    %% 2. Filtrage local multicritère (aucun appel API)
    Visiteur ->> Front: Appliquer filtres (prix, min_pers, allergènes, régime, thème)
    Note over Front: Filtrage local en mémoire<br/>(sans requête réseau)
    Front ->> Front: FiltrerMenus(criteres)
    Front -->> Visiteur: Actualiser instantanément la liste

    %% 3. Consultation du détail d'un menu
    Visiteur ->> Front: Cliquer sur un menu
    Front ->> API: GET /api/v1/menus/{id}
    API ->> BDD: ObtenirDetailCompletMenu(id)
    BDD -->> API: Detail (plats_inclus, descriptions, allergenes_precis)
    API -->> Front: 200 OK (detail_menu)
    Front -->> Visiteur: Afficher vue détaillée du menu

    %% 4. Action de commande avec condition d'authentification
    Visiteur ->> Front: Cliquer sur "Commander ce menu"
    Front ->> Auth: VerifierSessionActive()

    alt Utilisateur déjà connecté
        Auth -->> Front: Session valide (JWT actif)
        Front -->> Visiteur: Rediriger vers "/commande/nouvelle?menu_id={id}"
    else Visiteur non connecté
        Auth -->> Front: Aucune session
        Front -->> Visiteur: Rediriger vers "/connexion?redirect=/commande/nouvelle?menu_id={id}"
    end

```

---

## Parcours 2 : Inscription (Création de compte client)

### 1. Règles et données métier

* **Données requises :** Nom, prénom, adresse email valide, mot de passe.
* **Politique de mot de passe :** Minimum 10 caractères incluant au moins 1 majuscule, 1 minuscule, 1 chiffre et 1 caractère spécial (RGPD & ANSSI).
* **Rôle par défaut :** Attribué automatiquement au rôle Client (`user_role.CLIENT`).
* **Confirmation & Authentification :** Hachage salé du mot de passe (bcrypt), notification de bienvenue et remise immédiate d'un jeton JWT d'accès.

### 2. Diagramme de séquence Mermaid

```mermaid
sequenceDiagram
    autonumber
    actor Visiteur
    participant Front as Frontend (App/Web)
    participant API as Serveur API
    participant BDD as Base de Données (PostgreSQL)
    participant Mail as Service Email

    Visiteur ->> Front: Saisir formulaire (nom, prenom, email, password) et valider
    Front ->> API: POST /api/v1/auth/register (nom, prenom, email, password)
    
    API ->> BDD: VerifierEmailExiste(email)
    BDD -->> API: Email disponible (null)
    
    API ->> API: HasherMotDePasse(password)
    API ->> BDD: InsererUtilisateur(nom, prenom, email, hash, role='Client')
    BDD -->> API: UtilisateurCree(id)
    
    API ->> Mail: EnvoyerEmailBienvenue(email, prenom)
    Mail -->> API: EmailEnvoye
    
    API -->> Front: 201 Created (Token JWT, profil_utilisateur)
    Front -->> Visiteur: Rediriger vers l'espace client ou la commande en cours

```

---

## Parcours 3 : Prendre contact

### 1. Règles et données métier

* **Champs du formulaire :** Nom, prénom, email, numéro de téléphone (optionnel), objet du message, message.
* **Persistance NoSQL :** Stockage dans la collection MongoDB `contacts` pour un suivi et archivage sans altérer le schéma relationnel PostgreSQL.
* **Notifications :** Double envoi transactionnel (alerte interne à l'équipe + accusé de réception automatique au visiteur).

### 2. Diagramme de séquence Mermaid

```mermaid
sequenceDiagram
    autonumber
    actor Visiteur
    participant Front as Frontend (App/Web)
    participant API as Serveur API
    participant Mongo as BDD NoSQL (MongoDB)
    participant Mail as Service Email

    %% 1. Saisie et validation client
    Visiteur ->> Front: Saisir formulaire (nom, prenom, email, telephone, objet, message)
    Visiteur ->> Front: Cliquer sur "Envoyer le message"
    Note over Front: Validation syntaxique (email valide, champs requis)

    %% 2. Envoi et traitement serveur
    Front ->> API: POST /api/v1/contact (nom, prenom, email, telephone, objet, message)
    API ->> API: ValiderEtNettoyerDonnees()
    
    API ->> Mongo: insertOne({ nom, prenom, email, telephone, objet, message, traite: false, created_at: ISODate() })
    Mongo -->> API: Acknowledged (insertedId)

    %% 3. Notifications par email en parallèle
    par Notification gérance et accusé de réception
        API ->> Mail: EnvoyerAlerteEquipe(contact_data)
        Mail -->> API: MailEnvoye
    and Accusé de réception visiteur
        API ->> Mail: EnvoyerAccuseReception(email, prenom)
        Mail -->> API: MailEnvoye
    end

    %% 4. Confirmation utilisateur
    API -->> Front: 201 Created ("Message transmis avec succès")
    Front ->> Front: ReinitialiserFormulaire()
    Front -->> Visiteur: Afficher notification de succès

```