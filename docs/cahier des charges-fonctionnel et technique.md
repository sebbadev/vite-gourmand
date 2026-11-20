# Cahier des charges fonctionnel et technique — Vite & Gourmand

> Application web de commande de prestations traiteur et gestion événementielle.  
> Titre professionnel Développeur Web et Web Mobile (RNCP 37674).

---

## 1. Présentation générale et identité

### 1.1 Page d'accueil (Vitrine)
* **Présentation de l'entreprise :** Histoire, valeurs, mise en avant du savoir-faire et du professionnalisme de l'équipe.
* **Preuve sociale :** Affichage dynamique des avis clients vérifiés et modérés par l'équipe.
* **Appels à l'action (CTA) :** Accès direct au catalogue des menus et formulaire de contact.

### 1.2 Navigation principale
* Lien permanent vers l'accueil.
* Accès direct au catalogue complet des menus.
* Espace d'authentification (selon profil : Visiteur, Utilisateur, Employé, Administrateur).
* Lien vers le formulaire de contact.

### 1.3 Pied de page (Footer)
* Horaires d'ouverture et de livraison (du lundi au dimanche).
* Coordonnées complètes et contact d'urgence.
* Liens légaux obligatoires : Mentions légales, Politique de confidentialité (RGPD), Conditions Générales de Vente (CGV).

---

## 2. Catalogue et consultation des menus

### 2.1 Vue globale du catalogue
* Consultation libre ouverte aux visiteurs non authentifiés et aux utilisateurs connectés.
* Affichage sous forme de cartes : titre, vignette photo, description courte, nombre minimal de personnes, tarif de base et bouton « Voir le détail ».
* **Filtres de recherche dynamiques (sans rechargement de page) :**
  * Prix plafond et fourchette budgétaire.
  * Thématique événementielle (Noël, Pâques, Classique, Événement d'entreprise, etc.).
  * Régime alimentaire (Végétarien, Végan, Classique, Sans gluten).
  * Capacité minimale (nombre de personnes).

### 2.2 Fiche détaillée d'un menu
* Galerie photographique complète du menu.
* Description détaillée et composition par plat (Entrée, Plat principal, Dessert).
* **Mise en évidence des règles et contraintes :**
  * Tarif plancher (pour le nombre minimal de couverts requis).
  * Liste explicite des allergènes à déclaration obligatoire (règlementation européenne).
  * Conditions de conservation, stockage et délai minimal de prévenance pour la commande.
  * Stock et disponibilité sur la période.
* **Action de commande :** Bouton ouvrant le tunnel de commande pré-rempli. Si l'internaute est un visiteur non authentifié, une étape intermédiaire l'invite à se connecter ou à créer son compte.

---

## 3. Gestion des comptes et authentification

### 3.1 Profils et contrôle d'accès (RBAC)
* **Visiteur :** Consultation du catalogue, détails des menus, page contact.
* **Utilisateur (Client) :** Réservation, suivi de commandes, historique, dépôt d'avis.
* **Employé :** Gestion opérationnelle des menus/plats, mise à jour des statuts de commande, modération des avis.
* **Administrateur :** Supervision complète, création des comptes employés, métriques financières et analytiques.

### 3.2 Inscription et sécurité des identifiants
* **Données requises :** Nom, prénom, numéro de téléphone mobile, adresse email valide, mot de passe.
* **Politique de mot de passe :** Minimum 10 caractères, incluant au moins 1 majuscule, 1 minuscule, 1 chiffre et 1 caractère spécial.
* **Cycle de vie du compte :**
  * Attribution par défaut du rôle `Utilisateur`.
  * Envoi d'un email transactionnel de bienvenue à la création.
  * Procédure de réinitialisation de mot de passe par jeton temporaire envoyé par email.

---

## 4. Tunnel de commande et règles de gestion métier

### 4.1 Saisie de la prestation
* Pré-remplissage automatique des coordonnées client (nom, prénom, téléphone, email, adresse de livraison habituelle).
* Sélection obligatoire de la date et du créneau horaire de livraison souhaités.
* Sélection du nombre de convives (avec blocage strict en dessous du seuil minimal requis par le menu).

### 4.2 Règles de calcul (Tarification)
* `RG-01 (Prix de base)` : `Montant = Nombre de personnes × Prix unitaire par personne`.
* `RG-02 (Remise volume)` : Application automatique d'une remise de 10 % sur l'ensemble de la commande si le nombre de personnes sélectionné dépasse d'au moins 5 unités le minimum requis (`Nb_personnes >= Minimum + 5`).
* `RG-03 (Frais de livraison)` : Forfait fixe de 5,00 € + 0,59 € par kilomètre parcouru depuis le siège du restaurant.

---

## 5. Espaces dédiés et cycles de traitement

### 5.1 Espace Client (Utilisateur)
* Tableau de bord personnel avec mise à jour du profil et des adresses.
* Historique des commandes avec détail complet des prestations.
* **Règles d'intervention sur commande :**
  * Annulation autonome autorisée tant que la commande n'a pas atteint l'état « Acceptée ».
  * Modification des détails logistiques autorisée avant acceptation (hors changement de menu).
* **Suivi en temps réel :** Chronologie horodatée des changements de statut dès l'acceptation de la commande.
* **Avis post-prestation :** Déclenchement automatique d'un email dès passage au statut « Terminée », invitant le client à noter la prestation (1 à 5 étoiles) et déposer un commentaire.

### 5.2 Espace Collaborateur (Employé)
* Gestion du catalogue : création, modification et désactivation des menus, plats, ingrédients, allergènes et horaires d'ouverture.
* Filtrage multicritère des commandes (par statut, client, date de livraison).
* **Gestion des annulations :** Obligation de renseigner le motif d'annulation et la confirmation du contact préalable avec le client (appel mobile ou email).
* **Cycle de vie des statuts de commande :**
  1. `Acceptée`
  2. `En préparation`
  3. `En cours de livraison`
  4. `Livrée`
  5. `En attente de retour matériel` *(cas de prêt de vaisselle/chafing dish : notification automatique d'obligation de restitution sous 10 jours ouvrés, sous peine d'une indemnité forfaitaire de 600 € stipulée aux CGV)*.
  6. `Terminée` *(soit livraison simple sans matériel, soit validation de restitution du matériel)*.
* Modération et publication des avis clients en attente.

### 5.3 Espace Direction (Administrateur)
* Périmètre d'action incluant toutes les fonctions du rôle Employé.
* Gestion du personnel : création des accès employés (notification email sans mention du mot de passe en clair), désactivation immédiate des accès (départ ou révocation).
* Compte d'administration dédié (compte racine provisionné, création d'admin désactivée depuis l'interface publique).
* **Tableau de bord décisionnel & analytique :**
  * Volume de commandes par catégorie et par menu.
  * Analyse comparative via structure NoSQL/semi-structurée (agrégation document ou exploitation JSONB PostgreSQL).
  * Suivi du chiffre d'affaires consolidé par menu, par semaine et par mois.

---

## 6. Conformité, accessibilité et exigences non fonctionnelles

* **RGAA & Accessibilité :** Interface conforme aux critères du Référentiel Général d'Amélioration de l'Accessibilité (contrastes, navigation clavier, attributs ARIA).
* **RGPD :** Consentement explicite sur les formulaires, droit d'accès, de rectification et d'effacement des données personnelles.
* **Sécurité applicative :** Protection contre les injections SQL, failles XSS, CSRF, et stockage sécurisé des mots de passe hachés.
* **Disponibilité :** Déploiement en ligne continu et fonctionnel requis pour la recette finale.

---

## 7. Planification et livrables de certification DWWM

### 7.1 Phases de réalisation
1. Analyse du besoin et formalisation des spécifications.
2. Conception graphique, ergonomique et prototypage Figma.
3. Modélisation de la base de données et intégration des interfaces.
4. Développement des APIs REST, logique métier et sécurisation.
5. Recette, tests et déploiement continu.

### 7.2 Livrables attendus pour le jury
* **Dépôt Git :**
  * `README.md` complet détaillant l'installation et l'exécution locale.
  * Historique de commits conventionnels et branches structurées (`main`, `dev`, `feat/*`).
* **Livrables techniques et modélisation :**
  * Scripts SQL de création du schéma et jeu d'essai (*seed data*).
  * Modèle Conceptuel de Données (MCD) / Schéma Entité-Association.
  * Diagrammes de cas d'utilisation et diagrammes de séquence clés.
  * Justification écrite des choix technologiques et de sécurité.
* **Livrables design et utilisateur :**
  * Charte graphique complète et guide de styles (couleurs, typographies).
  * Wireframes et maquettes interactives (3 déclinaisons desktop, 3 déclinaisons mobile).
  * Manuel d'utilisation de l'application (incluant les comptes de test et rôles de démonstration).
* **Environnements distants :**
  * Lien d'accès vers l'application déployée en production/recette.
  * Lien vers l'espace de suivi de projet et carnet de produit (backlog).