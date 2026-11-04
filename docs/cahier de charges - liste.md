# Analyse cahier des charges

==================================================
## Page d'accueil
==================================================
* Présentation entreprise
* Mise en avant du professionnalisme de l’équipe
* Les avis clients qui sont validés


==================================================
## Menu de l’application
==================================================
* Retour vers la page d’accueil
* Accès à tous les menus
* Connexion (la connexion sera possible uniquement pour les employés, administrateurs et utilisateurs). Vous pouvez prendre la liberté de créer d’autres catégories que vous jugez nécessaires, mais veillez à respecter les aspects réglementaires (RGPD et sécurité)
* Accès à la page de contact


==================================================
## Pied de page
==================================================
* horaires lundi à dimanche
* lien vers mentions légales
* lien vers CGV


==================================================
## Vue globale de tous les menus
==================================================
* le titre et description de chaque menu + nb de pers min + prix + bouton details
* disponible pour utilisateur & visiteurs
* filtres pour recherches rapides
* prix maximum
* fourchette de prix
* thème
* régime
* nb de personne min,
* affichage dynamique sans recharger la page

==================================================
## Élément Menu
==================================================
* Configurable depuis l'espace administrateur par administrateur, restaurateur et employé
* Titre
* Galerie d'images
* Description
* Thème (Noël, Pâques, Anniversaire, Classique, Évènement)
* Liste de plats (entrée, plat principale, dessert)
* Nombre de personnes minimmum
* Prix pour le nombre de personnes minimale
* Liste d'allergène
* Conditions (par ex: temps de commande, précaution de stockage)
* Régime (végétarien, vegan, classique , autres)
* Stock disponible

==================================================
## Élément plat
==================================================
* Titre
* Galerie d'images
* Description
* Type de plat (entrée, plat principale ou dessert)
* Thème (Noël, Pâques, classique, évènement)
* Liste d'allergène
* Régime (végétarien, vegan, classique , autres)


==================================================
## Création de compte
==================================================
* nom + prénom
* téléphone mobile
* mot de passe sécurisé (10 caractères, min 1 spéciale, min 1 majuscule, min 1 minuscule, min 1 chiffre)
* rôle utilisateur
* mail de bienvenu automatique + validation


==================================================
## Connexion
==================================================
* username (=email)
* mot de passe
* réinitialisation de mot de passe avec bouton/lien, qui ouvre un champ pour saisir l'email, puis envoyer le lien de réinitialisation.


==================================================
## Vue détail de menu
==================================================
* tous les éléments du menu
* toutes les informations énumérées dans la bdd
* bouton de commande, qui ouvre l'espace commande avec le menu pré-rempli
* Si la personne est uniquement visiteur et non utilisateur, il lui sera demandé de se connecter ou de créer un compte, avant d'aller à la page de commande.
* Les conditions des menus doivent être mises bien en évidence. (prix, nb de pers min, allergènes, régimes, conditions)


==================================================
## Espace Commande de menu
==================================================
* On parvient à l'espace commande avec un bouton depuis vue global menus -> detail menu
* Le menu (pré-rempli)
* Informations de la prestation
* nom, prénom, mobile et mail (prérempli)
* adresse de livraison (prérempli)
* date et heure de livraison
* Nombre de personnes avec obligation du nombre minimale
* Calcule prix: nb de pers (x) le prix
* 10% de remise sur toute la commande si le nb de pers = + 5 du minimum.
* Livraison : 5 € + 0,59€ / km si la livraison est dans le zone définie.


==================================================
## Espace Utilisateur
==================================================
* Après connexion
* Modification des données personnelles
* Liste de commandes effectuées, avec les détails
* Annulation de commande possible tant que l'état n'est pas encore sur 'accepté'
* Modification de commande possible sauf le choix de menu
* Statut commande 'accepté' donne l'utilisateur accès au 'suivi' de l'état de commande.
* Le suivi énumère tous les états avec date et heure des modifications
* Quand la commande est "terminée", l'utilisateur est notifié par email pour donner son avis depuis la commande : une note de 1 à 5, suivi d'un commentaire.


==================================================
## Espace employé
==================================================
* Après connexion
* Modification suppression des menus, plats et horaires
* Il peut modifier / annuler une commande, mais seulement après avoir informé le client par mobile ou email du motif de l'annulation, ainsi que le mode 
  contact.
* Filtrage des commandes sur statut (état) ou client.
* Mise à jour des commandes des états
* "accepté"
* "en préparation"
* "en cours de livraison"
* "livré"
* "en attente de retour du matériel" avec notification par email des conditions -retour sous 10 jours ouvré, sous peine de 600€ de pénalités (mentionné 
	dans les CGV). 
   Le client doit répondre en prenant contact avec la société.
* "terminée" : soit livré sans prêt de matériel, soit matériel restitué.
* Validation ou refus des avis reçus des clients


==================================================
## Espace administrateur
==================================================
* Après connexion
* Création de type "employé" fournir un email + mot de passe
* l'employé est notifié par email sans le mot de passe
* rendre inutilisable un compte employé après un départ
* Création d'un compte pour José
* Il n'est pas possible de créer un compte administrateur depuis l'application
* Un administrateur peut faire tout ce qu'un employé peut faire
* Visualiser le nombre de commande par menu
* Comparaison entre eux via une graphique d'une base non relationnelle
* Calcul du chiffre d'affaires, par menu et par période.


==================================================
## Contact
==================================================
* Depuis le menu navigation
* Formulaire avec titre, description email pour la réponse
* Validation => envoie email à l'entreprise


==================================================
## Autres conditions
==================================================
* Déploiement de l'application avec pénalités si l'application n'est pas en ligne et fonctionnelle au moment de la livraison.
* L'application doit être accessible conformément au RGAA


==================================================
## Les étapes
==================================================
* Analyse des besoins
* Maquettage
* Intégration
* Développement des règles de gestion
* Déploiement


==================================================
## Intégrer sans la copie
==================================================
* Ls dispositions de sécurité
* Justifier les choix techniques (Il est très important de pouvoir justifier et exposer notre point de vue sur le différentes technologies).


==================================================
## Les livrables
==================================================
* Lien repo Git où se trouve le code du projet
	* Git README.md avec la démarche pour déployer l'application en local
	* Une branche principale
	* Une branche de développement
	* Chaque fonctionnalité sur une branche issue de la branche dev. Après test, merge vers branche dev
	* Une fois que la branche dev est testé correctement, effectuer une merge vers la branche principale
* Lien vers l'application déployée
* Lien vers le logiciel de gestion de projet
* Les fichiers.sql de création de BDD + l'intégration de données
* Manuel d'utilisation en pdf
	* Présentation de l'application
	* Identifiants d'administration
* Charte graphique en pdf
	* palette de couleurs
	* polices
	* wireframes & mockups : 3 maquettes bureautique, maquettes mobile
* Documentation traitant l'explication de gestion de projet


==================================================
## Documentation technique
==================================================
* Réflexion initiales technologiques
* Configuration de l'environnement de travail
* Modèle Conceptuel de Données ou diagramme de classes
* Diagramme d'utilisation ainsi que diagramme de séquence
* Documentation du déploiement de l'application, avec la démarche et les différentes étappes