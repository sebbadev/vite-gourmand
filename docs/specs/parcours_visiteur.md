Les parcours du visiteur :
Parcours 1 : Visiter la boutique, filtrer, consulter le détail
Parcours 2 : Inscription
Parcours 3 : Prendre contact


=========================================================================================================
Parcours 1 : Visiter la boutique, filtrer, consulter le détail et commander
=========================================================================================================
#1. Règles et données métier
	- Structure d'un Menu : un ou plusieurs plats, nombre minimal de personnes, prix, liste d'allergènes, régime alimentaire (ex. végétarien, sans gluten, halal), et au moins un thème (ex. mariage, soirée d'entreprise, anniversaire).

	- Filtres gérés en mémoire locale (côté client) : nombre de personnes, budget/prix, exclusion d'allergènes, régime, thème.

	- Navigation après clic « Commander » :
		* Si l'utilisateur possède déjà une session active (token valide) : redirection vers l'écran de création d'une nouvelle commande avec le menu présélectionné.
		* Sinon : redirection vers la mire de connexion (/connexion?redirect=/commande).

#2. Étapes textuelles (chemin nominal et alternatives)

	- Chargement initial : Le visiteur arrive sur la boutique. Le frontend récupère la liste des menus via l'API, les enregistre en mémoire vive (état local) et  es affiche.

	- Filtrage instantané (Front-only) : Le visiteur ajuste ses critères (nombre de personnes, budget max, allergènes à exclure, régime, thème). Le frontend applique les filtres en direct sur les menus en cache, sans appel réseau ni rechargement.

	- Consultation détaillée : Le visiteur clique sur un menu. Le frontend interroge GET /menus/{id}. L'API renvoie les détails complets (liste des plats qui composent le menu, description détaillée, liste exhaustive des allergènes). Le frontend affiche la vue détaillée.

	- Action « Commander » :
		* Le visiteur clique sur le bouton « Commander ce menu ».
		* Le frontend contrôle si un jeton d'authentification valide est présent en mémoire/stockage local.
		* Cas 1 (Connecté) : Redirection immédiate vers le tunnel de nouvelle commande (/commande/nouvelle?menuId=...).
		* Cas 2 (Non connecté) : Redirection vers la page de connexion (/login) avec mémorisation de l'intention de commande.


#3. Diagramme de séquence Mermaid
```mermaid
sequenceDiagram
    autonumber
    actor Visiteur
    participant Front as Frontend (App/Web)
    participant Auth as Gestionnaire Session
    participant API as Serveur API
    participant BDD as Base de Données

    %% 1. Chargement initial
    Visiteur ->> Front: Accéder à la boutique
    Front ->> API: GET /menus
    API ->> BDD: ObtenirMenusAvecMetadata()
    BDD -->> API: Menus (id, titre, prix, min_pers, regime, themes, allergenes)
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
    Front ->> API: GET /menus/{id}
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
        Front -->> Visiteur: Rediriger vers "/connexion?redirect=/commande"
    end



=========================================================================================================
### Parcours 2 : Inscription
=========================================================================================================
#1. Étapes textuelles (chemin nominal)
	- 	Le visiteur remplit le formulaire (nom, email, mot de passe) et valide.
	- 	Le frontend vérifie le format des champs et envoie les données à l'API.
	- 	L'API vérifie si l'adresse email existe déjà en base.
	-	L'API hache le mot de passe et crée le compte en base.
	-	L'API déclenche l'envoi d'un email de bienvenue (ou de confirmation).
	-	L'API renvoie une confirmation de succès avec le jeton de session (JWT).
	-	Le frontend connecte l'utilisateur et affiche le tableau de bord.


#2. Diagramme de séquence Mermaid : visiteur_inscription
```mermaid
	sequenceDiagram
	    autonumber
	    actor Visiteur
	    participant Front as Frontend (App/Web)
	    participant API as Serveur API
	    participant BDD as Base de Données
	    participant Mail as Service Email

	    Visiteur ->> Front: Saisir formulaire et cliquer sur "S'inscrire"
	    Front ->> API: POST /auth/register (email, password, nom)
	    
	    API ->> BDD: VerifierEmailExiste(email)
	    BDD -->> API: Email disponible (null)
	    
	    API ->> API: HasherMotDePasse(password)
	    API ->> BDD: InsererUtilisateur(email, hash, nom)
	    BDD -->> API: UtilisateurCree(id)
	    
	    API ->> Mail: EnvoyerEmailConfirmation(email, token)
	    Mail -->> API: EmailEnvoye
	    
	    API -->> Front: 201 Created (Token JWT, profil)
	    Front -->> Visiteur: Afficher confirmation et redirection



=========================================================================================================
    Parcours 3 : Prendre contact
=========================================================================================================
#1. Règles et données métier
	
	-	Champs du formulaire : Nom, prénom, email, numéro de téléphone (optionnel), objet du message (ex. Demande de devis événement, Renseignement 	allergènes, Autre), et corps du message.

	-	Sécurité & Intégrité :
		*	Validation des formats côté client (email valide, message non vide) pour un retour d'erreur immédiat.
		*	Validation stricte et assainissement côté serveur (sanitization anti-XSS).

	-	Traitements consécutifs :
		*	Sauvegarde du message en base de données (pour archivage et suivi dans le panneau d'administration).
		*	Notification email automatique transmise à l'équipe du restaurant.
		*	Email d'accusé de réception automatique envoyé au visiteur.

#2. Étapes textuelles (chemin nominal)
	-	Le visiteur accède à la page « Contact ».
	-	Le visiteur remplit le formulaire et clique sur « Envoyer le message ».
	-	Le frontend valide le format des champs saisis (email syntaxiquement correct, champs obligatoires renseignés).
	-	Le frontend transmet la requête POST /contact avec les données du formulaire à l'API.
	-	L'API vérifie et assainit le contenu reçu.
	-	L'API enregistre la demande dans la table contacts de la base de données.
	-	L'API déclenche deux actions via le service d'envoi d'emails :
		*	Envoi d'une alerte à l'équipe du restaurant avec le message et les coordonnées.
		*	Envoi d'un accusé de réception automatique au visiteur confirmant la bonne réception.
	-	L'API renvoie une réponse 201 Created au frontend.
	-	Le frontend affiche un message de succès (avec réinitialisation du formulaire) au visiteur.



#3. Diagramme de séquence Mermaid
```mermaid
sequenceDiagram
    autonumber
    actor Visiteur
    participant Front as Frontend (App/Web)
    participant API as Serveur API
    participant BDD as Base de Données
    participant Mail as Service Email

    %% 1. Saisie et validation client
    Visiteur ->> Front: Saisir formulaire (nom, email, objet, message)
    Visiteur ->> Front: Cliquer sur "Envoyer le message"
    Note over Front: Validation du format des champs<br/>(email valide, champs requis)

    %% 2. Envoi et traitement serveur
    Front ->> API: POST /contact (nom, email, objet, message)
    API ->> API: ValiderEtNettoyerDonnees()
    
    API ->> BDD: InsererDemandeContact(donnees)
    BDD -->> API: ConfirmationEnregistrement(id_message)

    %% 3. Notifications par email
    par Notification gérance et accusé de réception
        API ->> Mail: EnvoyerAlerteEquipe(contact_data)
        Mail -->> API: MailEnvoye
    and Accusé visiteur
        API ->> Mail: EnvoyerAccuseReception(email, nom)
        Mail -->> API: MailEnvoye
    end

    %% 4. Confirmation utilisateur
    API -->> Front: 201 Created
    Front ->> Front: ReinitialiserFormulaire()
    Front -->> Visiteur: Afficher notification de succès ("Message bien envoyé")