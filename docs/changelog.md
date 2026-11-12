# Changelog - Vite & Gourmand

## 🎯 Description du document

>Ce log enregistre tous les changements et leurs références effectués au cours du projet

---

## [Unreleased] - Phase 3 (Core Backend)

### Changed
- **Sécurité / Hachage :** Remplacement de `passlib` par `bcrypt` natif pour éliminer les bugs d'incompatibilité de version et garantir un hachage direct sécurisé ($2b$).
- **Sécurité / Tokens JWT :** Remplacement de `python-jose` par `PyJWT` (compatible RFC 7519, activement maintenu).

### Documentation
- Mise à jour du backlog de la tâche P3-03 (Sécurité & Authentification).

***

### Changed
* **Architecture / DTO :** Alignement du contrat d'API utilisateur sur le schéma Pydantic `UserResponse` (faisant office de `UserRead` dans la cartographie conceptuelle de `modele_donnees.md`), garantissant l'étanchéité stricte du mot de passe haché (`password_hash`).
* **Modélisation / Horodatage :** Typage de la colonne `heure_livraison` de l'entité `Commande` en `sa.Time()` (heure pure, ex: `12:30:00`) au lieu de `DateTime`, découplant l'heure de livraison de la `date_prestation` afin d'éliminer les dérives de fuseaux horaires (Timezone shifts) et s'aligner rigoureusement sur la migration Alembic `22d30dd5266f`.

***

### Added
* **Commandes / Modification avant acceptation (`PATCH /api/v1/commandes/{id}`) :** Ajout de la route permettant au client d'ajuster les paramètres logistiques (date, heure, adresse, distance) et les quantités de convives tant que la commande est au statut `En attente de validation`, avec blocage strict du changement de menu et réajustement automatique des stocks/tarifs (rattrapage d'une exigence du cahier des charges non modélisée dans les diagrammes de séquence initiaux).
