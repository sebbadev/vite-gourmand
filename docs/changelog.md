# Changelog - Vite & Gourmand

## 🎯 Description du document

> Ce log enregistre tous les changements et leurs références effectués au cours du projet selon les principes de *Keep a Changelog* et *SemVer* (*Semantic Versioning*).

---

## [Unreleased] - Phase 4 (Core Frontend Angular & Évolutions Back-Office)

### Added
- **Front-Office & Tunnel d'achat (Angular 18+) :** Catalogue dynamique avec filtres multi-critères temps réel, panier réactif (`CartService`) avec calcul de devis API (remise volume 10 % et frais kilométriques), et Espace Client (`/mon-compte`).
- **Back-Office Employé (`/employe`) :** Suivi et incrémentation rapide des statuts de commande, filtres multi-critères, CRUD (*Create, Read, Update, Delete* — création, lecture, mise à jour, suppression) complet des menus et plats, modération des avis MongoDB et gestion des horaires/messages.
- **Back-Office Administrateur (`/admin`) :** Gestion RH (*Ressources Humaines*) des comptes employés, tableau de bord analytique connecté aux pipelines d'agrégation MongoDB (`commandes_stats`), et gestion dynamique des référentiels (régimes alimentaires et thèmes événementiels).
- **API REST (*Representational State Transfer*) :** Ajout des points d'accès (*endpoints*) d'administration `POST` et `PUT` sous `/api/v1/admin/referentiels/{regimes|themes}` et exposition des coordonnées client dans le suivi des commandes back-office.
- **Assets & Médias :** Intégration des 14 visuels optimisés au format WebP (*Web Picture format*) dans `frontend/public/assets/images/` (menus et plats), image de secours (*fallback* SVG inline) sur le catalogue et documentation des crédits photographiques (`docs/credits-medias.md`).

### Fixed
- **Configuration Git :** Ancrage de `/admin/` à la racine dans `.gitignore` afin d'inclure le module frontend `frontend/src/app/features/admin/`.
- **Affichage Galerie (`menu-detail.scss`) :** Ajustement du ratio (`aspect-ratio: 4 / 3`) et du centrage (`object-position: center center`) de la photographie principale pour éviter le rognage des visuels de plats.

---

## [Unreleased] - Phase 3 (Core Backend)

### Changed
- **Sécurité / Hachage :** Remplacement de `passlib` par `bcrypt` natif pour éliminer les bugs d'incompatibilité de version et garantir un hachage direct sécurisé (`$2b`).
- **Sécurité / Tokens JWT :** Remplacement de `python-jose` par `PyJWT` (compatible RFC 7519, activement maintenu).
- **Architecture / DTO :** Alignement du contrat d'API utilisateur sur le schéma Pydantic `UserResponse` (faisant office de `UserRead` dans la cartographie conceptuelle de `modele_donnees.md`), garantissant l'étanchéité stricte du mot de passe haché (`password_hash`).
- **Modélisation / Horodatage :** Typage de la colonne `heure_livraison` de l'entité `Commande` en `sa.Time()` (heure pure, ex: `12:30:00`) au lieu de `DateTime`, découplant l'heure de livraison de la `date_prestation` afin d'éliminer les dérives de fuseaux horaires (*Timezone shifts*) et s'aligner rigoureusement sur la migration Alembic `22d30dd5266f`.

### Added
- **Commandes / Modification avant acceptation (`PATCH /api/v1/commandes/{id}`) :** Ajout de la route permettant au client d'ajuster les paramètres logistiques (date, heure, adresse, distance) et les quantités de convives tant que la commande est au statut `En attente de validation`, avec blocage strict du changement de menu et réajustement automatique des stocks/tarifs (rattrapage d'une exigence du cahier des charges non modélisée dans les diagrammes de séquence initiaux).

### Documentation
- Mise à jour du backlog de la tâche P3-03 (Sécurité & Authentification).