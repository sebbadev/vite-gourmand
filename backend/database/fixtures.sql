-- ========================================================
-- Jeu d'essai initial (Fixtures) : Vite & Gourmand
-- Mot de passe par défaut pour tous les comptes : Password123!
-- Hash bcrypt ($2b$12$) vérifié : $2b$12$L73.bKkIeW8n4tZ22vK/z.v5sVfK0n2E2x2P.H2G6iP8fD1W4k7Xe
-- ========================================================

-- 1. Référentiels : Allergènes
INSERT INTO public.allergenes (allergene_id, libelle) VALUES
(1, 'Gluten'),
(2, 'Crustacés'),
(3, 'Œufs'),
(4, 'Poissons'),
(5, 'Arachides'),
(6, 'Soja'),
(7, 'Lait'),
(8, 'Fruits à coque'),
(9, 'Moutarde'),
(10, 'Graines de sésame');

-- 2. Référentiels : Régimes
INSERT INTO public.regimes (regime_id, libelle) VALUES
(1, 'Végétarien'),
(2, 'Végétalien (Vegan)'),
(3, 'Sans gluten'),
(4, 'Sans lactose'),
(5, 'Halal'),
(6, 'Casher');

-- 3. Référentiels : Thèmes
INSERT INTO public.themes (theme_id, libelle) VALUES
(1, 'Mariage & Réception'),
(2, 'Cocktail Entreprise'),
(3, 'Buffet Champêtre'),
(4, 'Gala Événementiel'),
(5, 'Anniversaire');

-- 4. Horaires d'ouverture
INSERT INTO public.horaires (jour, heure_ouverture, heure_fermeture) VALUES
('Lundi', '08:00:00', '19:00:00'),
('Mardi', '08:00:00', '19:00:00'),
('Mercredi', '08:00:00', '19:00:00'),
('Jeudi', '08:00:00', '20:00:00'),
('Vendredi', '08:00:00', '22:00:00'),
('Samedi', '07:30:00', '23:00:00'),
('Dimanche', '08:00:00', '16:00:00');

-- 5. Utilisateurs (Comptes de test pour chaque rôle)
INSERT INTO public.utilisateurs (user_id, email, password_hash, prenom, nom, telephone, adresse, code_postal, ville, pays, role) VALUES
(1, 'admin@vite-gourmand.fr', '$2b$12$L73.bKkIeW8n4tZ22vK/z.v5sVfK0n2E2x2P.H2G6iP8fD1W4k7Xe', 'Sophie', 'Directrice', '0601020304', '14 Rue de la Paix', '75002', 'Paris', 'France', 'Administrateur'),
(2, 'employe@vite-gourmand.fr', '$2b$12$L73.bKkIeW8n4tZ22vK/z.v5sVfK0n2E2x2P.H2G6iP8fD1W4k7Xe', 'José', 'Collaborateur', '0611223344', '22 Avenue Foch', '75016', 'Paris', 'France', 'Employé'),
(3, 'client.durand@example.com', '$2b$12$L73.bKkIeW8n4tZ22vK/z.v5sVfK0n2E2x2P.H2G6iP8fD1W4k7Xe', 'Marc', 'Durand', '0655443322', '5 Boulevard Victor Hugo', '92200', 'Neuilly-sur-Seine', 'France', 'Client'),
(4, 'client.leroy@example.com', '$2b$12$L73.bKkIeW8n4tZ22vK/z.v5sVfK0n2E2x2P.H2G6iP8fD1W4k7Xe', 'Claire', 'Leroy', '0677889900', '18 Rue des Lilas', '94300', 'Vincennes', 'France', 'Client');

-- 6. Plats élémentaires
INSERT INTO public.plats (plat_id, titre, type_de_plat, images_url) VALUES
(1, 'Carpaccio de Saint-Jacques au citron vert', 'Entrée', '/assets/images/plats/carpaccio-st-jacques.webp'),
(2, 'Velouté de potimarron et éclats de châtaigne', 'Entrée', '/assets/images/plats/veloute-potimarron.webp'),
(3, 'Salade croquante de quinoa aux agrumes', 'Entrée', '/assets/images/plats/salade-quinoa.webp'),
(4, 'Filet de bœuf rôti sauce morilles', 'Plat principal', '/assets/images/plats/filet-boeuf-morilles.webp'),
(5, 'Pavé de saumon sauvage rôti et herbes fraîches', 'Plat principal', '/assets/images/plats/pave-saumon.webp'),
(6, 'Mijoté de lentilles corail au curry doux et coco', 'Plat principal', '/assets/images/plats/curry-lentilles.webp'),
(7, 'Écrasé de pommes de terre à la truffe d''été', 'Accompagnement', '/assets/images/plats/ecrase-truffe.webp'),
(8, 'Poêlée printanière d''asperges et fèves', 'Accompagnement', '/assets/images/plats/poelee-legumes.webp'),
(9, 'Fondant pur cacao et coulis de framboises', 'Dessert', '/assets/images/plats/fondant-chocolat.webp'),
(10, 'Tartelette sablée au citron meringuée', 'Dessert', '/assets/images/plats/tartelette-citron.webp'),
(11, 'Salade de fruits de saison parfumée à la menthe', 'Dessert', '/assets/images/plats/salade-fruits.webp');

-- 7. Liaisons Plats <-> Allergènes (Tous les plats couverts)
INSERT INTO public.plats_allergenes (plat_id, allergene_id) VALUES
(1, 2),        -- Saint-Jacques : Crustacés
(2, 7),        -- Velouté : Lait
(4, 7),        -- Bœuf morilles : Lait
(5, 4),        -- Saumon : Poissons
(9, 1), (9, 3), (9, 7),    -- Fondant : Gluten, Œufs, Lait
(10, 1), (10, 3), (10, 7); -- Tartelette : Gluten, Œufs, Lait

-- 8. Liaisons Plats <-> Régimes (Tous les plats couverts)
INSERT INTO public.plats_regimes (plat_id, regime_id) VALUES
(2, 1), (2, 3),                 -- Velouté : Végétarien, Sans gluten
(3, 1), (3, 2), (3, 3), (3, 4), -- Salade quinoa : Végétarien, Vegan, Sans gluten, Sans lactose
(6, 1), (6, 2), (6, 3), (6, 4), -- Curry lentilles : Végétarien, Vegan, Sans gluten, Sans lactose
(7, 1),                         -- Écrasé truffe : Végétarien
(8, 1), (8, 2), (8, 3), (8, 4), -- Poêlée asperges : Végétarien, Vegan, Sans gluten, Sans lactose
(9, 1),                         -- Fondant : Végétarien
(10, 1),                        -- Tartelette : Végétarien
(11, 1), (11, 2), (11, 3), (11, 4); -- Salade fruits : Végétarien, Vegan, Sans gluten, Sans lactose

-- 9. Liaisons Plats <-> Thèmes (Tous les plats couverts)
INSERT INTO public.plats_themes (plat_id, theme_id) VALUES
(1, 1), (1, 4),  -- Saint-Jacques : Mariage, Gala
(2, 2), (2, 3),  -- Velouté : Cocktail Entreprise, Buffet Champêtre
(3, 2), (3, 3),  -- Salade quinoa : Cocktail Entreprise, Buffet Champêtre
(4, 1), (4, 4),  -- Bœuf morilles : Mariage, Gala
(5, 2), (5, 3),  -- Saumon : Cocktail Entreprise, Buffet Champêtre
(6, 2), (6, 3),  -- Curry lentilles : Cocktail Entreprise, Buffet Champêtre
(7, 1), (7, 4),  -- Écrasé truffe : Mariage, Gala
(8, 2), (8, 4),  -- Poêlée asperges : Cocktail Entreprise, Gala
(9, 1), (9, 5),  -- Fondant : Mariage, Anniversaire
(10, 2), (10, 5), -- Tartelette : Cocktail Entreprise, Anniversaire
(11, 3), (11, 5); -- Salade fruits : Buffet Champêtre, Anniversaire

-- 10. Menus composés
INSERT INTO public.menus (menu_id, titre, nombre_personnes_min, prix_par_personne, description, quantite_disponible, images_url, is_active) VALUES
(1, 'Menu Prestige des Grands Jours', 10, 48.00, 'Une sélection raffinée associant Saint-Jacques et bœuf truffé pour des événements d''exception.', 150, '/assets/images/menus/prestige.webp', true),
(2, 'Menu Cocktail Signature', 15, 32.50, 'Formule dînatoire complète idéale pour les soirées professionnelles et réceptions d''entreprise.', 300, '/assets/images/menus/cocktail.webp', true),
(3, 'Menu Champêtre & Végétal', 8, 26.00, 'Élaboré intégralement à partir de produits frais de saison, labellisé végétarien et sans gluten.', 100, '/assets/images/menus/vegetal.webp', true);

-- 11. Liaisons Menus <-> Plats
INSERT INTO public.menus_plats (menu_id, plat_id) VALUES
-- Menu 1 : Prestige
(1, 1), (1, 4), (1, 7), (1, 9),
-- Menu 2 : Cocktail Signature
(2, 2), (2, 5), (2, 8), (2, 10),
-- Menu 3 : Champêtre & Végétal
(3, 2), (3, 3), (3, 6), (3, 11);

-- 12. Liaisons Menus <-> Thèmes
INSERT INTO public.menus_themes (menu_id, theme_id) VALUES
(1, 1), (1, 4),
(2, 2), (2, 4),
(3, 3), (3, 5);

-- 13. Commandes de démonstration
INSERT INTO public.commandes (commande_id, numero_commande, user_id, date_prestation, heure_livraison, prix_total, remise_appliquee, adresse_livraison, distance_km, frais_livraison, statut, date_commande, statut_paiement, statut_materiel, contact_client_effectue) VALUES
(1, 'CMD-2026-0001', 3, '2026-10-15', '12:30:00', 960.00, 0.0, '5 Boulevard Victor Hugo, 92200 Neuilly-sur-Seine', 8.5, 12.50, 'Terminée', '2026-10-01 09:15:00+02', 'Réglée', 'Retourné', false),
(2, 'CMD-2026-0002', 4, '2026-11-20', '19:30:00', 1170.00, 130.00, '18 Rue des Lilas, 94300 Vincennes', 14.0, 18.00, 'Acceptée', '2026-11-02 14:20:00+01', 'En attente de règlement', 'Inclus', false),
(3, 'CMD-2026-0003', 3, '2026-11-05', '11:30:00', 260.00, 0.0, '5 Boulevard Victor Hugo, 92200 Neuilly-sur-Seine', 8.5, 12.50, 'Annulée', '2026-10-28 16:45:00+01', 'Annulée', 'Non inclus', true);

UPDATE public.commandes 
SET motif_annulation = 'Impossibilité technique suite à panne de chambre froide.', 
    mode_contact_annulation = 'Téléphone' 
WHERE commande_id = 3;

INSERT INTO public.commande_details (detail_id, commande_id, menu_id, quantite, prix_applique) VALUES
(1, 1, 1, 20, 48.00),
(2, 2, 2, 40, 32.50),
(3, 3, 3, 10, 26.00);

-- 14. Avis clients
INSERT INTO public.avis (avis_id, description, user_id, menu_id, statut, qualite, service, prix) VALUES
(1, 'Prestation irréprochable. Le bœuf aux morilles a fait l''unanimité auprès de nos convives.', 3, 1, 'Approuvé', 'Excellent', 'Excellent', 'Bien');

-- 15. Réalignement des séquences d'identifiants (Auto-increment)
SELECT setval('public.utilisateurs_user_id_seq', (SELECT MAX(user_id) FROM public.utilisateurs));
SELECT setval('public.menus_menu_id_seq', (SELECT MAX(menu_id) FROM public.menus));
SELECT setval('public.plats_plat_id_seq', (SELECT MAX(plat_id) FROM public.plats));
SELECT setval('public.allergenes_allergene_id_seq', (SELECT MAX(allergene_id) FROM public.allergenes));
SELECT setval('public.regimes_regime_id_seq', (SELECT MAX(regime_id) FROM public.regimes));
SELECT setval('public.themes_theme_id_seq', (SELECT MAX(theme_id) FROM public.themes));
SELECT setval('public.horaires_horaire_id_seq', (SELECT MAX(horaire_id) FROM public.horaires));
SELECT setval('public.commandes_commande_id_seq', (SELECT MAX(commande_id) FROM public.commandes));
SELECT setval('public.commande_details_detail_id_seq', (SELECT MAX(detail_id) FROM public.commande_details));
SELECT setval('public.avis_avis_id_seq', (SELECT MAX(avis_id) FROM public.avis));