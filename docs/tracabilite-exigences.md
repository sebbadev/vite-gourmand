# Matrice de Traçabilité des Exigences — Vite & Gourmand

> **Document de cadrage et de recette technique (P0-05)**  
> Référence méthodologique : Titre Professionnel Développeur Web et Web Mobile (RNCP 37674).  
> Ce document établit la correspondance stricte entre les exigences du cahier des charges client, les Règles de Gestion (RG) associées et les solutions techniques mises en œuvre (Architecture, API, Base de données et Front-end).

---

## 1. Exigences Fonctionnelles & Règles de Gestion Métier

| Réf. Exigence | Description du Besoin Client | Règle de Gestion (RG) | Solution Technique & Composants | Statut |
| :--- | :--- | :--- | :--- | :--- |
| **EX-F01** | Consultation libre du catalogue par les visiteurs sans compte obligatoire. | **RG-01 :** Menus publics consultables avec prix/pers, nb min personnes, allergènes, régimes et thèmes. | Endpoint public `GET /api/v1/menus`, composant Angular `CatalogListComponent`. | Validé |
| **EX-F02** | Filtrage dynamique du catalogue (prix, régime, allergène, thème, nb personnes). | **RG-02 :** Filtrage instantané réactif côté client sans recharger la page. | Service Angular réactif (`BehaviorSubject`), filtrage en mémoire locale (Pipe / Signals). | Validé |
| **EX-F03** | Inscription et connexion sécurisée des clients. | **RG-03 :** Mot de passe supérieur ou égal à 10 car. (maj, min, chiffre, car. spécial). Hachage sécurisé. | `POST /api/v1/auth/register`, hachage bcrypt / Argon2, jetons `JWT Bearer`. | Validé |
| **EX-F04** | Demande de commande avec calcul automatique du prix de base. | **RG-04 :** Prix base = $\text{prix\_par\_personne} \times \text{quantité}$. | Table `commandes`, endpoint `POST /api/v1/commandes`, service `PricingService`. | Validé |
| **EX-F05** | Remise commerciale sur volume de commande. | **RG-05 :** Remise de 10 % appliquée sur le montant des menus si le total dépasse le seuil défini. | Calcul côté API dans `PricingService`, champ `remise_appliquee` dans PostgreSQL. | Validé |
| **EX-F06** | Calcul kilométrique des frais de livraison. | **RG-06 :** Forfait de base + coût par km au-delà de la zone locale de gratuité. | Intégration géolocalisation / calcul distance, champ `frais_livraison` et `distance_km`. | Validé |
| **EX-F07** | Validation ou refus des commandes par l'équipe du restaurant. | **RG-07 :** Statut initial `En attente de validation`. Acceptation émet le lien de paiement ; refus exige motif et réincrémente le stock. | `PATCH /api/v1/admin/commandes/{id}/statut`, machine d'état `OrderStatus`, réincrémentation `menus.quantite_disponible`. | Validé |
| **EX-F08** | Interdiction d'annuler une commande acceptée sans contact préalable. | **RG-08 :** Obligation d'attester d'un contact téléphonique ou par email avant toute annulation d'une commande validée. | Champs d'audit obligatoires : `motif_annulation`, `mode_contact_annulation`, `contact_client_effectue = true`. | Validé |
| **EX-F09** | Mise à disposition et restitution du matériel de réception (chafing dish, vaisselle). | **RG-09 :** Statut `Inclus`. Restitution obligatoire sous 10 jours ouvrés, sous peine de 600 € d'indemnité forfaitaire. | Énumération `Equipment` (`INCLUS`, `RETOURNE`, `NON_INCLUS`), alerte email à $J+10$, facture pénalité. | Validé |
| **EX-F10** | Clôture finale de la commande (`Terminée`). | **RG-10 :** La commande bascule au statut `Terminée` uniquement si `Livrée` + `Réglée` + `Matériel Retourné`. | Contrôle d'intégrité multicritère dans `OrderService`, archivage de clôture. | Validé |
| **EX-F11** | Émission de la facture téléchargeable en PDF. | **RG-11 :** Facture disponible dès le statut `Livrée`, portant la mention *"À RÉGLER"* ou *"ACQUITTÉE"*. | Service `PdfService` (ReportLab / WeasyPrint), endpoint `GET /api/v1/commandes/{id}/facture`. | Validé |
| **EX-F12** | Formulaire de contact public pour demandes spécifiques et devis. | **RG-12 :** Transmission du message à l'équipe avec accusé de réception automatique au visiteur. | `POST /api/v1/contact`, persistance dans collection MongoDB `contacts`, double notification email. | Validé |
| **EX-F13** | Dépôt et modération des avis clients suite à une prestation. | **RG-13 :** Seul un client ayant une commande `Terminée` peut évaluer (notes 1 à 5 + avis). Modération avant publication. | Collection MongoDB `avis`, statut initial `En attente`, modération back-office (`Approuvé` / `Rejeté`). | Validé |
| **EX-F14** | Tableaux de bord et métriques de pilotage pour l'administrateur. | **RG-14 :** Visualisation du CA consolidé, volume par menu et paniers moyens par période (semaine/mois/année). | Pipeline d'agrégation MongoDB `$match`, `$group` sur la collection dénormalisée `commandes_stats`. | Validé |

---

## 2. Exigences Non Fonctionnelles & Contraintes Techniques

| Réf. Exigence | Domaine | Contrainte Technique & Norme | Implémentation dans le Projet | Statut |
| :--- | :--- | :--- | :--- | :--- |
| **EX-NF01** | Architecture | Séparation stricte Front-end / Back-end (API REST découplée). | Front Angular (Standalone Components) / API Python (FastAPI). | Validé |
| **EX-NF02** | Persistance Polyglotte | Coexistence obligatoire d'une BDD relationnelle et non relationnelle. | **PostgreSQL** (ACID / Commandes / Catalogue) + **MongoDB** (Avis / Contacts / Analytics). | Validé |
| **EX-NF03** | Sécurité (OWASP) | Protection contre les injections SQL, failles XSS, CSRF et énumération de comptes. | Requêtes paramétrées via SQLAlchemy ORM, DTOs Pydantic, messages d'erreurs génériques à l'authentification. | Validé |
| **EX-NF04** | Accessibilité (RGAA) | Conformité avec les critères du RGAA (contrastes, navigation clavier, sémantique). | Balisage HTML5 sémantique, attributs ARIA, ratios de contrastes vérifiés sur la charte graphique. | Validé |
| **EX-NF05** | Données Personnelles (RGPD) | Consentement explicite et droit de suppression des données. | Checkbox de consentement RGPD sur les formulaires, soft delete (`is_deleted = true`). | Validé |
| **EX-NF06** | Déploiement & Disponibilité | Déploiement en ligne continu et opérationnel requis pour la soutenance. | API déployée sur Render/Railway, Front sur Vercel/Render, PostgreSQL et MongoDB Atlas en cloud. | En cours |
| **EX-NF07** | Versionnage & Méthodologie | Historique Git rigoureux, commits conventionnels et branches dédiées. | Arborescence de branches (`main`, `dev`, `docs/*`, `feat/*`), merges explicites `--no-ff`. | Validé |