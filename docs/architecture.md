Vite & Gourmand - architecture

1. Arborescense des dossiers et fichiers
2. Correspondance & Cartographie des Données (Mapping Multicouche)




### 2. Correspondance & Cartographie des Données (Mapping Multicouche)

> Cette cartographie formalise la continuité des données à travers les différentes couches de l'application : la persistance relationnelle (PostgreSQL), le mapping objet-relationnel (SQLAlchemy), les contrats de validation d'API (Pydantic) et la persistance orientée document (MongoDB).

## Entité 1 : Utilisateur
Rôle métier : Gestion des comptes, authentification JWT et contrôle des accès selon les rôles.
Table PostgreSQL : utilisateurs
Modèle ORM SQLAlchemy : models.Utilisateur
Schémas DTO Pydantic : UserBase, UserCreate, UserRead
MongoDB : — (non concerné)

## Entité 2 : Menu
Rôle métier : Produit principal du catalogue commercial, gestion des portions et décrémentation des stocks.
Table PostgreSQL : menus
Modèle ORM SQLAlchemy : models.Menu
Schémas DTO Pydantic : MenuBase, MenuRead
MongoDB : Référencé sous forme dénormalisée dans la collection commandes_stats.

## Entité 3 : Plat
Rôle métier : Composant culinaire élémentaire assemblé dans les menus ; support des régimes et allergènes.
Table PostgreSQL : plats
Modèle ORM SQLAlchemy : models.Plat
Schémas DTO Pydantic : PlatBase, PlatRead
MongoDB : — (non concerné)

## Entité 4 : Commande
Rôle métier : Suivi transactionnel, logistique de livraison, caution matériel et audit d'annulation.
Table PostgreSQL : commandes
Modèle ORM SQLAlchemy : models.Commande
Schémas DTO Pydantic : CommandeBase, CommandeRead
MongoDB : Projetée au statut Terminée dans la collection commandes_stats.

## Entité 5 : Détail de Commande (Ligne Panier)
Rôle métier : Association entre une commande et les menus choisis, avec figeage du prix facturé.
Table PostgreSQL : commande_details
Modèle ORM SQLAlchemy : models.CommandeDetail
Schémas DTO Pydantic : CommandeDetailBase
MongoDB : Intégré comme tableau imbriqué (menus: [...]) dans commandes_stats.

## Entité 6 : Avis Client
Rôle métier : Notation multicritère (qualité, service, prix), retour d'expérience et workflow de modération.
Table PostgreSQL : avis (table miroir / intégrité relationnelle)
Modèle ORM SQLAlchemy : models.Avis
Schémas DTO Pydantic : AvisBase, AvisRead
MongoDB : Collection avis (source de données active et modération en direct).

## Entité 7 : Horaire
Rôle métier : Plages horaires d'ouverture et de commande du restaurant traiteur.
Table PostgreSQL : horaires
Modèle ORM SQLAlchemy : models.Horaire
Schémas DTO Pydantic : HoraireBase, HoraireRead
MongoDB : — (non concerné)

## Entité 8 : Référentiels (Thèmes, Régimes, Allergènes)
Rôle métier : Taxonomie pour la recherche multicritère et la sécurité alimentaire des clients.
Tables PostgreSQL : themes, regimes, allergenes
Modèles ORM SQLAlchemy : models.Theme, models.Regime, models.Allergene
Schémas DTO Pydantic : ThemeBase, RegimeBase, AllergeneBase
MongoDB : — (non concerné)

## Entité 9 : Statistiques Décisionnelles (Reporting Admin)
Rôle métier : Agrégation des volumes de vente et calculs de chiffre d'affaires pour les graphiques administrateur.
Table PostgreSQL : — (aucune requête analytique lourde sur l'OLTP)
Modèle ORM SQLAlchemy : —
Schémas DTO Pydantic : StatsResponse, DatasetGraphique
MongoDB : Collection commandes_stats (pipeline d'agrégation $match, $group).