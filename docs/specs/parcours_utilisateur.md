Les parcours de l'utilisateur (client connecté):

> Cet acteur hérite des parcours publics documentés dans `parcours_visiteurs.md`
	-	Visiter la boutique, filtrer, consulter le détail
	-	se connecter
	-	prendre contact

Parcours supplémentaires:
Parcours 1 : Se connecter (Authentification)
Parcours 2 : Réinitialiser son mot de passe
Parcours 3 : Passer commande + payer sa commande
Parcours 4 : Suivre l'état de sa commande
Parcours 5 : Restitutionner son matériel emprunté
Parcours 6 : Voir l'historique des commandes
Parcours 7 : Modifier les informations de son compte


=========================================================================================================
Parcours 1 : Se connecter (Authentification)
=========================================================================================================
#1. Règles et données métier
	-	Identifiants requis : Email et mot de passe.
	-	Mécanisme d'authentification : Vérification de l'existence du compte, comparaison sécurisée de l'empreinte du mot de passe (via hachage salé type Argon2 ou bcrypt).
	-	Gestion de session : Génération d'un jeton d'accès sécurisé (JWT ou cookie HTTP-only sécurisé).
	-	Cas d'erreur géré : Si l'email est inconnu ou si le mot de passe est faux, le message d'erreur doit être générique (« Identifiants invalides ») pour ne pas révéler si l'email existe ou non (bonne pratique de sécurité).

#2. Étapes textuelles
	-	L'utilisateur accède à la page de connexion.
	-	Il saisit son email et son mot de passe, puis clique sur « Se connecter ».
	-	Le frontend valide le format des champs saisis et envoie une requête POST /auth/login à l'API.
	-	L'API recherche l'utilisateur en base de données par son email.
	
	Vérification des identifiants :
	-	Cas nominal (Succès) : Le compte existe et l'empreinte du mot de passe correspond. L'API génère un jeton JWT contenant l'identifiant et le rôle de l'utilisateur.
	-	Cas d'échec : L'email est introuvable ou le mot de passe ne correspond pas. L'API renvoie une erreur 401 Unauthorized.
	
	-	En cas de succès, l'API renvoie le statut 200 OK avec le token et le profil minimal.
	-	Le frontend enregistre la session et redirige l'utilisateur vers sa page d'origine, ou son tableau de bord.

---------------------------------
#3. Diagramme de séquence Mermaid
```mermaid
sequenceDiagram
    autonumber
    actor Client as Utilisateur
    participant Front as Frontend (App/Web)
    participant API as Serveur API
    participant BDD as Base de Données

    %% 1. Saisie et transmission
    Client ->> Front: Saisir email et mot de passe
    Client ->> Front: Cliquer sur "Se connecter"
    Note over Front: Vérification syntaxique (email valide, mot de passe non vide)
    Front ->> API: POST /auth/login (email, password)

    %% 2. Recherche et contrôle d'empreinte
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


=========================================================================================================
Parcours 2 : Réinitialiser son mot de passe
=========================================================================================================
#1. Règles et données métier
	-	Sécurité anti-énumération : Si l'adresse email n'existe pas en base, l'API renvoie quand même un message de succès générique (« Si cet email existe, un lien vous a été envoyé »). Cela empêche un attaquant de sonder quels emails sont inscrits sur la plateforme.

	-	Jeton de réinitialisation (Reset Token) :
		*	À usage unique.
		*	Durée de validité courte (ex. 15 à 30 minutes).
		*	Stocké sous forme hachée en base pour éviter toute compromission en cas de fuite de données.

	-	Validation du nouveau mot de passe : Respect des contraintes de robustesse (longueur minimale, caractères spéciaux, etc.) et hachage avant persistance en base.

#2. Étapes textuelles
	Phase A : Demande de réinitialisation
	-	L'utilisateur clique sur « Mot de passe oublié ? » et renseigne son adresse email.
	-	Le frontend valide le format de l'email et envoie une requête POST /auth/forgot-password.
	-	L'API recherche l'utilisateur en base :
		*	Si trouvé : L'API génère un token aléatoire sécurisé, définit une date d'expiration (ex. 15 min), enregistre l'empreinte du token en base et déclenche l'envoi de l'email avec le lien unique (https://.../reinitialiser-mdp?token=xyz).
		*	Si non trouvé : L'API ne fait rien de particulier (ou logue l'événement), mais répond exactement de la même manière.
	-	L'API renvoie un statut 200 OK avec un message générique.
	-	Le frontend affiche un message invitant l'utilisateur à vérifier sa boîte de réception pour le lien de réinitialisation.

	Phase B : Définition du nouveau mot de passe
	-	L'utilisateur clique sur le lien reçu dans l'email et arrive sur la page de saisie avec le jeton dans l'URL.
	-	L'utilisateur saisit son nouveau mot de passe (et confirmation) puis valide.
	-	Le frontend contrôle la cohérence des mots de passe et transmet POST /auth/reset-password avec le jeton et le nouveau mot de passe.
	-	L'API vérifie la validité du jeton en base (existence, non-expiration, non encore utilisé).
		Contrôle du jeton :
		*	Si valide : L'API hache le nouveau mot de passe, met à jour le compte, révoque le jeton utilisé (ainsi que les éventuelles sessions actives antérieures) et renvoie un 200 OK.
		*	Si invalide ou expiré : L'API renvoie une erreur 400 Bad Request (« Jeton invalide ou expiré »).
	-	Le frontend affiche la confirmation et invite l'utilisateur à se connecter.


#3 Diagramme de séquence Mermaid
```mermaid
sequenceDiagram
    autonumber
    actor Client as Utilisateur
    participant Front as Frontend (App/Web)
    participant API as Serveur API
    participant BDD as Base de Données
    participant Mail as Service Email

    %% ===================================================
    %% PHASE A : Demande de réinitialisation
    %% ===================================================
    rect rgb(245, 247, 250)
    Note over Client, Mail: PHASE A : Demande du lien de réinitialisation
    Client ->> Front: Saisir email et cliquer sur "Réinitialiser"
    Front ->> API: POST /auth/forgot-password (email)
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

    %% ===================================================
    %% PHASE B : Saisie du nouveau mot de passe
    %% ===================================================
    rect rgb(240, 249, 255)
    Note over Client, Mail: PHASE B : Validation du nouveau mot de passe
    Client ->> Front: Cliquer sur le lien dans l'email (/reset-password?token=xyz)
    Front -->> Client: Afficher formulaire de nouveau mot de passe

    Client ->> Front: Saisir nouveau mot de passe et confirmer
    Note over Front: Vérification de correspondance et robustesse
    Front ->> API: POST /auth/reset-password (token, nouveauPassword)

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


=========================================================================================================
Parcours 3 : Passer commande et payer sa commande
=========================================================================================================

#1. Règles et données métier
	La bonne pratique d'architecture : Séparer les 3 statuts
	En base de données, la table Commande doit comporter trois machines à états distinctes :
	-	statut_commande : EN_ATTENTE_VALIDATION => ACCEPTEE (ou REFUSEE) => EN_PREPARATION => EN_LIVRAISON => LIVREE => TERMINEE (ou ANNULEE).

	-	statut_paiement : EN_ATTENTE => PAYE_EN_LIGNE ou PAYE_LIVRAISON.

	-	statut_materiel : AUCUN => A_RESTITUER => RESTITUE (ou EN_RETARD_PENALITE).

	La commande passe au statut final TERMINEE uniquement lorsque :statut_commande = LIVREE ET statut_paiement = PAYE ET statut_materiel = RESTITUE

#2. Étapes textuelles 
	-	Soumission de la commande : Le client configure son panier et clique sur « Valider la commande » (sans saisie bancaire immédiate).

	-	Contrôles automatiques backend : L'API vérifie les disponibilités (menus, stocks matériel, créneau, statut du compte client).

	-	Enregistrement initial :
		*	statut_commande : EN_ATTENTE_VALIDATION
		*	statut_paiement : EN_ATTENTE
		*	statut_materiel : NON_LIVRE

	-	Accusé de réception client : L'API confirme la bonne prise en compte de la demande (écran + email).

	-	Alerte restaurant : L'API notifie le restaurateur / régisseur avec le détail et les indicateurs de disponibilité.

	-	Décision du restaurateur :
		*	Cas Refus : Le restaurateur clique sur « Refuser » (avec motif). L'API notifie le client et clôture la demande.
		*	Cas Acceptation : Le restaurateur clique sur « Accepter ».

	-	Traitement après acceptation :
		*	statut_commande passe à ACCEPTEE.
		*	L'API génère un lien de paiement sécurisé unique et envoie un email/SMS au client (« Commande confirmée - Lien de paiement disponible »).

	-	Préparation et expédition (indépendamment du paiement) :
		*	La cuisine prépare la commande (EN_PREPARATION).
		*	Le livreur prend en charge la commande (EN_LIVRAISON).

	-	Livraison & encaissement éventuel :
		*	Le livreur remet les plats et le matériel au client.
		*	Paiement : Le client règle soit par terminal auprès du livreur (qui marque PAYE_LIVRAISON), soit le client paie plus tard via le lien en ligne (PAYE_EN_LIGNE).
		*	Le matériel passe à l'état A_RESTITUER (compte à rebours de 10 jours activé avec mention des pénalités).

	-	Restitution & Clôture :
		*	Dès que le matériel est retourné et contrôlé, statut_materiel passe à RESTITUE.
		*	Une fois payée ET matériel restitué, la commande passe au statut final TERMINEE.


#3. Diagramme de séquence Mermaid
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

    %% -----------------------------------------------------------
    %% 1. SOUMISSION ET VALIDATION DISPONIBILITÉ
    %% -----------------------------------------------------------
    rect rgb(245, 247, 250)
    Note over Client, BDD: 1. Demande de commande (sans paiement direct)
    Client ->> Front: Valider la commande (panier, date, adresse)
    Front ->> API: POST /commandes (panier, date_livraison, adresse)

    API ->> BDD: VerifierDispoEtEligibilite(date, menus, materiel, client_id)
    BDD -->> API: EtatDisponibilites

    API ->> BDD: InsererCommande(statut_cmd: "EN_ATTENTE_VALIDATION", statut_paie: "EN_ATTENTE", statut_mat: "NON_LIVRE")
    BDD -->> API: CommandeCreee(id_commande)

    API ->> Mail: EnvoyerAccuseReception(client_email, id_commande)
    API -->> Front: 201 Created (id_commande, statut: "EN_ATTENTE_VALIDATION")
    Front -->> Client: Afficher "Commande en cours de validation par le restaurant"
    end

    %% -----------------------------------------------------------
    %% 2. DÉCISION DU RESTAURATEUR
    %% -----------------------------------------------------------
    rect rgb(254, 249, 235)
    Note over Resto, API: 2. Validation par l'équipe du restaurant
    API ->> Resto: NotifierNouvelleCommande(id_commande, recap_dispos)

    alt Restaurateur REFUSE la commande
        Resto ->> API: POST /commandes/{id}/refuser (motif)
        API ->> BDD: MajStatuts(statut_cmd: "REFUSEE")
        API ->> Mail: NotifierRefusClient(client_email, motif)
        API -->> Resto: 200 OK
    else Restaurateur ACCEPTE la commande
        Resto ->> API: POST /commandes/{id}/accepter
        API ->> BDD: MajStatuts(statut_cmd: "ACCEPTEE")
        API ->> Banque: GenererLienPaiementUnique(id_commande, montant)
        Banque -->> API: url_paiement
        API ->> Mail: EnvoyerConfirmationEtLienPaiement(client_email, url_paiement)
        API -->> Resto: 200 OK
    end
    end

    %% -----------------------------------------------------------
    %% 3. CYCLE DE PRÉPARATION ET LIVRAISON
    %% -----------------------------------------------------------
    rect rgb(240, 249, 255)
    Note over Resto, Livreur: 3. Préparation et acheminement (flux physique)
    Resto ->> API: PUT /commandes/{id}/statut (statut_cmd: "EN_PREPARATION")
    Resto ->> API: PUT /commandes/{id}/statut (statut_cmd: "PRETE")
    
    API ->> Livreur: AssignerLivraison(id_commande, adresse)
    Livreur ->> Resto: RecupererCommandeEtMateriel()
    Livreur ->> API: PUT /commandes/{id}/statut (statut_cmd: "EN_LIVRAISON")

    Livreur ->> Client: Remettre repas + matériel
    Livreur ->> API: POST /commandes/{id}/confirmer-livraison
    API ->> BDD: MajStatuts(statut_cmd: "LIVREE", statut_mat: "A_RESTITUER", date_max_restitution: J+10)
    API ->> Mail: NotifierLivraisonEffectueeEtRappelMateriel(client_email, delai: "10 jours", penalite: "600€")
    end

    %% -----------------------------------------------------------
    %% 4. PAIEMENT (LIVRAISON OU EN LIGNE)
    %% -----------------------------------------------------------
    rect rgb(245, 255, 245)
    Note over Client, Banque: 4. Règlement de la commande (asynchrone)
    alt Paiement sur place avec le livreur
        Client ->> Livreur: Régler par TPE / Espèces
        Livreur ->> API: POST /commandes/{id}/encaisser (mode: "SUR_PLACE")
        API ->> BDD: MajStatutPaiement("PAYE_LIVRAISON")
    else Paiement en ligne via le lien
        Client ->> Banque: Ouvrir lien et payer par CB
        Banque ->> API: POST /webhooks/paiement (event: payment_intent.succeeded)
        API ->> BDD: MajStatutPaiement("PAYE_EN_LIGNE")
    end
    end

    %% -----------------------------------------------------------
    %% 5. RESTITUTION DU MATÉRIEL ET CLÔTURE
    %% -----------------------------------------------------------
    rect rgb(255, 245, 245)
    Note over Client, BDD: 5. Restitution du matériel sous 10 jours
    Client ->> Resto: Restituer le matériel emprunté
    Resto ->> API: POST /commandes/{id}/restitution-materiel (etat: "CONFORME")
    API ->> BDD: MajStatutMateriel("RESTITUE")

    %% Vérification des conditions de clôture
    API ->> BDD: VerifierEligibiliteCloture(id_commande)
    Note over API, BDD: Condition : statut_cmd="LIVREE" ET statut_paie="PAYE" ET statut_mat="RESTITUE"
    API ->> BDD: MajStatutCommande("TERMINEE")
    API ->> Mail: EnvoyerRecuEtClotureDossier(client_email)
    end


=========================================================================================================
Parcours 4 : Suivre l'état de sa commande
=========================================================================================================
#1. Règles et données métier
	-	Accès sécurisé : L'utilisateur ne peut consulter que ses propres commandes (contrôle d'autorisation par jeton JWT ou session).

	-	Visibilité multicritère : L'écran de suivi expose clairement :
		*	La progression de la commande (EN_ATTENTE_VALIDATION => ACCEPTEE => EN_PREPARATION => EN_LIVRAISON => LIVREE => TERMINEE).
		*	L'état du règlement (EN_ATTENTE, PAYE_EN_LIGNE, PAYE_LIVRAISON). Si impayé, un bouton direct « Payer maintenant » reste accessible.
		*	L'état du matériel consigné/prêté (NON_LIVRE, A_RESTITUER, RESTITUE) avec rappel de la date limite (J+10) dès que la commande est livrée.

	-	Mode d'actualisation :
		*	Consultation manuelle par requête HTTP GET /commandes/{id}.
		*	Mise à jour proactive optionnelle : par rafraîchissement périodique (polling) ou réception de notifications / WebSocket lors des changements d'état majeurs.

#2. Étapes textuelles
	-	Le client accède à la page de détail d'une commande (via son espace client ou en cliquant sur le lien reçu par email/SMS).

	-	Le frontend vérifie la présence du token de session et transmet la requête GET /commandes/{id} avec le header d'autorisation.

	-	L'API vérifie que la commande demandée appartient bien à l'utilisateur authentifié (userId == commande.clientId).

	-	Vérification des droits :
		*	Cas non autorisé : Si la commande n'appartient pas au client, l'API renvoie une erreur 403 Forbidden.
		*	Cas autorisé : L'API extrait les détails et l'historique des statuts en base de données.

	-	L'API renvoie le statut 200 OK avec les données structurées :	
		*	Progression de préparation et coordonnées/créneau de livraison.
		*	Statut du paiement (et lien de paiement si toujours impayé).
		*	Statut du matériel (liste des équipements prêtés, date limite de restitution, avertissement des 10 jours).

	-	Le frontend affiche la frise chronologique d'avancement et les actions contextuelles (ex : « Payer ma commande », « Contacter le support »).


#3. Diagramme de séquence Mermaid
```mermaid
sequenceDiagram
    autonumber
    actor Client as Utilisateur
    participant Front as Frontend (App/Web)
    participant API as Serveur API
    participant BDD as Base de Données

    %% 1. Demande de consultation
    Client ->> Front: Accéder à la page "Suivi de commande" (/commandes/{id})
    Front ->> API: GET /commandes/{id} (Headers: Authorization Bearer Token)

    %% 2. Contrôle d'accès et récupération
    API ->> BDD: ObtenirCommandeEtStatuts(id)
    BDD -->> API: Commande (clientId, statut_cmd, statut_paie, statut_mat, date_livraison, items)

    alt Utilisateur non propriétaire de la commande
        API -->> Front: 403 Forbidden ("Accès refusé")
        Front -->> Client: Afficher message d'erreur et redirection
    else Utilisateur autorisé
        API ->> BDD: ObtenirHistoriqueEtDelaisMateriel(id)
        BDD -->> API: HistoriqueEtDelais (timeline, date_max_restitution)

        API -->> Front: 200 OK (details_commande, statuts, date_max_restitution, lien_paiement)
        
        Front ->> Front: ConstruireVueSuivi(timeline, statuts)
        Front -->> Client: Afficher frise chronologique & état des 3 statuts

        opt Commande livrée avec matériel à restituer
            Note over Front, Client: Alerte visuelle : "Matériel à restituer avant le [Date à J+10]"
        end

        opt Paiement toujours en attente
            Note over Front, Client: Bouton d'action actif : "Payer ma commande en ligne"
        end
    end



=========================================================================================================
Parcours 5 : Restituer son matériel emprunté
=========================================================================================================
#1. Règles et données métier
	-	Délai contractuel : 10 jours calendaires maximum à compter de la date de livraison.

	-	Modes de retour :
		*	Option 1 : Dépôt direct au restaurant par le client.
		*	Option 2 : Enlèvement sur place par un livreur (optionnel ou planifié lors de la livraison initiale).

	-	Contrôle qualitatif par le restaurateur :
		*	Conforme & complet : statut_materiel passe à RESTITUE.
		*	Dégradé ou manquant : Signalement avec constat chiffré (facturation du remplacement selon barème CGV).

	-	Contrôle d'échéance : 
		*	Retour sous =<10 jours : Clôture normale sans frais.
		*	Dépassement > 10 jours (ou non restitué) : Déclenchement d'un litige / application de la pénalité contractuelle (600 € prévus aux CGV).

	-	Condition de clôture globale :
		statut_commande = TERMINEE if statut_cmd = LIVREE and statut_paiement in {PAYE_EN_LIGNE}, PAYE_LIVRAISON} and statut_mat = RESTITUE

#2. Étapes textuelles
	-	Initiation du retour :
		*	Le client consulte son espace « Matériel à restituer », visualise les éléments empruntés et la date butoir. Il signale qu'il dépose le matériel au restaurant (ou génère un bon/code de retour).

	-	Réception physique :
		*	Le client remet les caisses/contenants au personnel du restaurant.

	-	Contrôle & saisie de conformité :
		*	L'employé du restaurant ouvre l'interface de gestion de la commande (/admin/commandes/{id}/restitution).
		*	L'employé inspecte les éléments et valide le retour (conforme / non conforme).

	-	Appel API de restitution :
		*	Le frontend du restaurant transmet POST /commandes/{id}/restitution avec l'état constaté (CONFORME ou INCOMPLET_CASSE).

	-	Traitement backend :
		*	L'API compare la date du jour avec la date_max_restitution (date de livraison + 10 jours).
		*	Cas nominal (Dans les délais & conforme) :
			*	L'API met à jour statut_materiel à RESTITUE.
			*	L'API vérifie si le paiement de la commande a déjà été soldé :
				*	Si oui : statut_commande bascule immédiatement à TERMINEE.
				*	Si non : statut_commande reste à LIVREE en attente du règlement final.
			*	Envoi d'un email de quittance de retour au client.

		*	Cas dégradé (Retard > 10 jours ou matériel détérioré) :
			*	L'API bascule statut_materiel en LITIGE_PENALITE.
			*	Création d'une facture d'indemnité / pénalité (selon barème CGV).
			*	Envoi d'un email de notification d'anomalie/pénalité au client.

	-	Confirmation finale : L'API confirme l'opération au restaurant et le client voit son espace actualisé en direct.


#3. Diagramme de séquence Mermaid
```mermaid
sequenceDiagram
    autonumber
    actor Client as Utilisateur
    actor Resto as Restaurateur / Employé
    participant FrontResto as Interface Resto (Back-office)
    participant API as Serveur API
    participant BDD as Base de Données
    participant Mail as Service Email

    %% 1. Remise physique
    Client ->> Resto: Déposer le matériel emprunté (avec réf commande)
    Resto ->> Resto: Inspecter l'état du matériel (complet, propre, non cassé)

    %% 2. Enregistrement par l'équipe
    Resto ->> FrontResto: Saisir réf commande et résultat contrôle
    FrontResto ->> API: POST /commandes/{id}/restitution (statut_retour: "CONFORME")

    %% 3. Vérifications en base
    API ->> BDD: ObtenirCommandePourRestitution(id)
    BDD -->> API: Commande (statut_paie, date_livraison, date_max_restitution)

    API ->> API: VerifierDelai(date_actuelle <= date_max_restitution)

    alt Matériel restitué à temps (<= 10 jours) et conforme
        API ->> BDD: MajStatutMateriel(id, "RESTITUE")
        
        %% Vérification si la commande peut être définitivement clôturée
        alt Paiement déjà soldé
            API ->> BDD: MajStatutCommande(id, "TERMINEE")
            Note over API, BDD: Commande 100% soldée et archivée
        else Paiement encore en attente
            Note over API: Commande reste à "LIVREE" jusqu'au paiement
        end

        API ->> Mail: EnvoyerAccuseRestitutionConforme(client_email, id)
        API -->> FrontResto: 200 OK ("Restitution validée avec succès")
        FrontResto -->> Resto: Afficher confirmation écran

    else Dépassement de délai (> 10 jours) ou matériel dégradé
        API ->> BDD: MajStatutMateriel(id, "LITIGE_PENALITE")
        API ->> BDD: CreerFacturePenalite(id, motif: "Non-restitution ou dégradation")
        API ->> Mail: EnvoyerNotificationPenalite(client_email, id, montant: "600€")
        API -->> FrontResto: 200 OK ("Dossier basculé en litige / pénalité")
        FrontResto -->> Resto: Alerte "Dossier pénalité généré"
    end


=========================================================================================================
Parcours 6 : Voir l'historique des commandes
=========================================================================================================
#1. Règles et données métier
	-	Cloisonnement des données : 
		L'utilisateur ne peut lister que les commandes rattachées à son propre user_id (contrôle strict via le token de session).

	-	Pagination & Performance : 
		La liste est paginée côté serveur (ex. 10 commandes par page) pour éviter de surcharger la base de données.

	-	Affichage synthétique : Chaque ligne de commande expose :
		*	Le numéro de commande et la date de passage.
		*	Le récapitulatif des menus et le montant total TTC.
		*	Les 3 statuts métier : progression (statut_cmd), paiement (statut_paie), et matériel (statut_mat).

	-	Condition d'émission de la facture :
		*	La facture devient exigible et téléchargeable dès que la commande passe au statut LIVREE (ou TERMINEE)
		*	Si la commande n'a pas encore été payée (statut_paie = EN_ATTENTE), le document PDF comporte le filigrane et la mention légale « Facture à 
			régler » ainsi que les coordonnées de paiement / date d'échéance.
		*	Si la commande a été payée, le document PDF affiche la mention « Facture acquittée » avec la date et le mode de règlement.
		*	Si la commande est encore en cours de préparation ou non validée (statut_cmd !== LIVREE), la facture n'est pas encore émise (seul un bon de
			commande / récapitulatif est visible).

#2. Étapes textuelles
	-	Accès à la section : L'utilisateur clique sur « Mes commandes » depuis son menu profil.

	-	Requête initiale : Le frontend transmet GET /commandes?page=1&limit=10 avec le jeton d'authentification.

	-	Contrôle et récupération :
		*	L'API extrait l'identifiant du client depuis le token JWT.
		*	L'API interroge la base de données pour récupérer les commandes avec status de ce client triées de la plus récente à la plus ancienne.

	-	Réponse synthétique : L'API renvoie un statut 200 OK avec le tableau des commandes et les métadonnées de pagination (total_pages, page_courante).

	-	Affichage : Le frontend présente la liste synthétique avec les badges de statut appropriés.

	-	Action contextuelle - Téléchargement des factures :
		*	L'utilisateur clique sur l'icône « Facture (PDF) » sur une commande.
		*	Le frontend appelle GET /commandes/{id}/facture.
		*	L'API vérifie que la commande est bien en statut >='LIVREE' et appartient au client.
		*	L'API génère (ou récupère depuis le stockage objet) le fichier PDF et le renvoie avec l'en-tête Content-Type: application/pdf.
		*	Le navigateur déclenche le téléchargement du document.

#3. Diagramme de séquence Mermaid
```mermaid
sequenceDiagram
    autonumber
    actor Client as Utilisateur
    participant Front as Frontend (App/Web)
    participant API as Serveur API
    participant BDD as Base de Données
    participant Storage as Service Factures / PDF

    %% 1. Consultation de la liste des commandes
    Client ->> Front: Accéder à "Mes commandes"
    Front ->> API: GET /commandes?page=1&limit=10 (Header: Bearer Token)

    API ->> API: ExtraireUserIdDepuisToken()
    API ->> BDD: ObtenirCommandesClient(userId, page=1, limit=10)
    BDD -->> API: ListeCommandes (id, date, montant, statuts, date_livraison) + TotalCount

    API -->> Front: 200 OK (commandes, pagination)
    Front ->> Front: GenererVueHistorique(commandes)
    Front -->> Client: Afficher liste des commandes avec statuts

    %% 2. Téléchargement de la facture (Dès livraison)
    opt Télécharger une facture
        Client ->> Front: Cliquer sur "Télécharger facture (PDF)"
        Front ->> API: GET /commandes/{id}/facture (Header: Bearer Token)

        API ->> BDD: VerifierStatutCommande(id, userId)
        BDD -->> API: Commande (statut_cmd, statut_paie, montant, client_data)

        alt Commande déjà livrée (statut_cmd in ["LIVREE", "TERMINEE"])
            %% [MODIFIÉ] Distinction selon l'état du paiement
            alt Commande non payée (statut_paie = "EN_ATTENTE")
                API ->> Storage: GenererFacturePDF(id, mention: "À RÉGLER", date_echeance)
            else Commande déjà réglée (statut_paie in ["PAYE_EN_LIGNE", "PAYE_LIVRAISON"])
                API ->> Storage: GenererFacturePDF(id, mention: "ACQUITTÉE", date_reglement)
            end

            Storage -->> API: FluxFichierPDF (buffer / url)
            API -->> Front: 200 OK (application/pdf, facture_{id}.pdf)
            Front -->> Client: Déclencher téléchargement du document PDF

        else Commande non encore livrée (statut_cmd < "LIVREE")
            API -->> Front: 400 Bad Request ("Facture disponible dès la livraison effective")
            Front -->> Client: Notification "Votre facture sera générée à la livraison"
        end
    end



=========================================================================================================
Parcours 7 : Modifier les informations de son compte
=========================================================================================================

#1. Règles et données métier
	-	Accès authentifié obligatoire : Toute modification exige un jeton JWT valide (ou cookie de session sécurisé).

	-	Données modifiables :
		*	Informations générales : Nom, prénom, téléphone, adresse de livraison habituelle / facturation.
		*	Sécurité (Mot de passe) : Modification conditionnée à la saisie et vérification préalable du mot de passe actuel.
		*	Email (Règle de sécurité) : L'email sert d'identifiant unique. S'il est modifiable, il nécessite de vérifier l'absence de doublon en base et
			l'envoi d'un lien de confirmation à la nouvelle adresse avant validation définitive.

	-	Intégrité et sécurité :
		*	Validation du format des données côté client et re-validation stricte côté API.
		*	Hachage salé du nouveau mot de passe (Argon2 ou bcrypt) avant écriture en base.
		*	Envoi d'un email de notification de sécurité au client lors de tout changement d'informations critiques (mot de passe ou email).

#2. Étapes textuelles
	-	Accès au profil : L'utilisateur clique sur « Mon profil » / « Paramètres du compte ».

	-	Chargement des données : Le frontend envoie GET /utilisateurs/me avec le token d'authentification. L'API renvoie les informations actuelles (hors 
		données sensibles comme le mot de passe).

	-	Cas A : Modification des coordonnées générales (Nom, téléphone, adresse) :
		*	L'utilisateur met à jour ses champs et clique sur « Enregistrer les modifications ».
		*	Le frontend valide les formats et envoie PATCH /utilisateurs/me avec le payload des données modifiées.
		*	L'API valide les données et met à jour l'enregistrement en base.
		*	L'API renvoie un statut 200 OK avec le profil actualisé.
		*	Le frontend affiche un message de confirmation vert.
	
	-	Cas B : Modification du mot de passe :
		*	L'utilisateur renseigne : mot de passe actuel, nouveau mot de passe et confirmation.
		*	Le frontend vérifie que le nouveau mot de passe respecte la politique de robustesse et que les deux saisies concordent.
		*	Le frontend envoie PATCH /utilisateurs/me/mot-de-passe (ancien_mot_de_passe, nouveau_mot_de_passe).
		*	L'API récupère le hash du mot de passe actuel en base et compare.
			*	Échec : Si l'ancien mot de passe est faux, l'API renvoie 400 Bad Request (« Le mot de passe actuel est incorrect »).
			*	Succès : L'API génère le hash du nouveau mot de passe, le persiste en base, et ordonne au service mail d'envoyer un email d'alerte sécurité 
				("Votre mot de passe vient d'être modifié").

	-	L'API renvoie 200 OK.
	
	-	Le frontend confirme la modification à l'utilisateur.

#3. Diagramme de séquence Mermaid
```mermaid