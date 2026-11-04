-- ========================================================
-- Script d'initialisation de la base : Vite & Gourmand
-- ========================================================

-- 1. Nettoyage
DROP TABLE IF EXISTS public.menus_plats CASCADE;
DROP TABLE IF EXISTS public.menus_themes CASCADE;
DROP TABLE IF EXISTS public.plats_allergenes CASCADE;
DROP TABLE IF EXISTS public.plats_regimes CASCADE;
DROP TABLE IF EXISTS public.plats_themes CASCADE;
DROP TABLE IF EXISTS public.commande_details CASCADE;
DROP TABLE IF EXISTS public.commandes CASCADE;
DROP TABLE IF EXISTS public.avis CASCADE;
DROP TABLE IF EXISTS public.horaires CASCADE;
DROP TABLE IF EXISTS public.plats CASCADE;
DROP TABLE IF EXISTS public.menus CASCADE;
DROP TABLE IF EXISTS public.allergenes CASCADE;
DROP TABLE IF EXISTS public.regimes CASCADE;
DROP TABLE IF EXISTS public.themes CASCADE;
DROP TABLE IF EXISTS public.utilisateurs CASCADE;

DROP TYPE IF EXISTS public.dish_types CASCADE;
DROP TYPE IF EXISTS public.equipment CASCADE;
DROP TYPE IF EXISTS public.notes CASCADE;
DROP TYPE IF EXISTS public.order_status CASCADE;
DROP TYPE IF EXISTS public.payment_status CASCADE;
DROP TYPE IF EXISTS public.review_status CASCADE;
DROP TYPE IF EXISTS public.user_role CASCADE;
DROP TYPE IF EXISTS public.contact_mode CASCADE;

-- 2. Types ENUM
CREATE TYPE public.dish_types AS ENUM ('Entrée', 'Plat principal', 'Accompagnement', 'Dessert');
CREATE TYPE public.equipment AS ENUM ('Inclus', 'Non inclus', 'Retourné');
CREATE TYPE public.notes AS ENUM ('Critique', 'À améliorer', 'Correct', 'Bien', 'Excellent');
CREATE TYPE public.order_status AS ENUM ('En attente de validation', 'Acceptée', 'Annulée', 'En préparation', 'En cours de livraison', 'Livrée', 'Terminée');
CREATE TYPE public.payment_status AS ENUM ('En attente de règlement', 'Annulée', 'Réglée');
CREATE TYPE public.review_status AS ENUM ('En attente', 'Approuvé', 'Répondu', 'Rejeté');
CREATE TYPE public.user_role AS ENUM ('Administrateur', 'Employé', 'Client');
CREATE TYPE public.contact_mode AS ENUM ('Téléphone', 'Email');

-- 3. Tables principales

CREATE TABLE public.utilisateurs (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    prenom VARCHAR(50) NOT NULL,
    nom VARCHAR(50) NOT NULL,
    telephone VARCHAR(50),
    adresse VARCHAR(255),
    code_postal VARCHAR(50),
    ville VARCHAR(50),
    pays VARCHAR(50),
    role public.user_role DEFAULT 'Client'::public.user_role NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT false
);

CREATE INDEX ix_utilisateurs_email ON public.utilisateurs (email);
CREATE INDEX ix_utilisateurs_id ON public.utilisateurs (user_id);

CREATE TABLE public.menus (
    menu_id SERIAL PRIMARY KEY,
    titre VARCHAR(50) NOT NULL,
    nombre_personnes_min INTEGER NOT NULL,
    prix_par_personne DOUBLE PRECISION NOT NULL,
    description TEXT NOT NULL,
    quantite_disponible INTEGER NOT NULL,
    images_url VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT false
);

CREATE INDEX ix_menus_menu_id ON public.menus (menu_id);

CREATE TABLE public.plats (
    plat_id SERIAL PRIMARY KEY,
    titre VARCHAR(50) NOT NULL,
    type_de_plat public.dish_types NOT NULL,
    images_url VARCHAR(255)
);

CREATE INDEX ix_plats_plat_id ON public.plats (plat_id);

CREATE TABLE public.allergenes (
    allergene_id SERIAL PRIMARY KEY,
    libelle VARCHAR(50) NOT NULL
);

CREATE TABLE public.regimes (
    regime_id SERIAL PRIMARY KEY,
    libelle VARCHAR(50) NOT NULL
);

CREATE TABLE public.themes (
    theme_id SERIAL PRIMARY KEY,
    libelle VARCHAR(50) NOT NULL
);

CREATE TABLE public.horaires (
    horaire_id SERIAL PRIMARY KEY,
    jour VARCHAR(50) NOT NULL,
    heure_ouverture TIME WITHOUT TIME ZONE NOT NULL,
    heure_fermeture TIME WITHOUT TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT false
);

CREATE TABLE public.commandes (
    commande_id SERIAL PRIMARY KEY,
    numero_commande VARCHAR(50) NOT NULL UNIQUE,
    user_id INTEGER NOT NULL REFERENCES public.utilisateurs(user_id),
    date_prestation DATE NOT NULL,
    heure_livraison TIMESTAMP WITH TIME ZONE NOT NULL,
    prix_total DOUBLE PRECISION NOT NULL,
    remise_appliquee DOUBLE PRECISION DEFAULT 0.0,
    adresse_livraison VARCHAR(255),
    distance_km DOUBLE PRECISION DEFAULT 0.0,
    frais_livraison DOUBLE PRECISION DEFAULT 5.0,
    statut public.order_status DEFAULT 'En attente de validation'::public.order_status,
    date_commande TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    statut_paiement public.payment_status DEFAULT 'En attente de règlement'::public.payment_status NOT NULL,
    statut_materiel public.equipment DEFAULT 'Inclus'::public.equipment NOT NULL,
    motif_annulation TEXT,
    mode_contact_annulation public.contact_mode,
    contact_client_effectue BOOLEAN DEFAULT false,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT false
);

CREATE INDEX ix_commandes_id ON public.commandes (commande_id);

CREATE TABLE public.commande_details (
    detail_id SERIAL PRIMARY KEY,
    commande_id INTEGER NOT NULL REFERENCES public.commandes(commande_id) ON DELETE CASCADE,
    menu_id INTEGER NOT NULL REFERENCES public.menus(menu_id),
    quantite INTEGER NOT NULL,
    prix_applique DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT false
);

CREATE INDEX ix_commande_details_id ON public.commande_details (detail_id);

CREATE TABLE public.avis (
    avis_id SERIAL PRIMARY KEY,
    description TEXT NOT NULL,
    user_id INTEGER REFERENCES public.utilisateurs(user_id),
    menu_id INTEGER REFERENCES public.menus(menu_id),
    statut public.review_status DEFAULT 'En attente'::public.review_status,
    qualite public.notes,
    service public.notes,
    prix public.notes,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT false
);

CREATE INDEX ix_avis_id ON public.avis (avis_id);

-- 4. Tables de liaison (n-n)

CREATE TABLE public.menus_plats (
    menu_id INTEGER NOT NULL REFERENCES public.menus(menu_id) ON DELETE CASCADE,
    plat_id INTEGER NOT NULL REFERENCES public.plats(plat_id) ON DELETE CASCADE,
    PRIMARY KEY (menu_id, plat_id)
);

CREATE TABLE public.menus_themes (
    menu_id INTEGER NOT NULL REFERENCES public.menus(menu_id) ON DELETE CASCADE,
    theme_id INTEGER NOT NULL REFERENCES public.themes(theme_id) ON DELETE CASCADE,
    PRIMARY KEY (menu_id, theme_id)
);

CREATE TABLE public.plats_allergenes (
    plat_id INTEGER NOT NULL REFERENCES public.plats(plat_id) ON DELETE CASCADE,
    allergene_id INTEGER NOT NULL REFERENCES public.allergenes(allergene_id) ON DELETE CASCADE,
    PRIMARY KEY (plat_id, allergene_id)
);

CREATE TABLE public.plats_regimes (
    plat_id INTEGER NOT NULL REFERENCES public.plats(plat_id) ON DELETE CASCADE,
    regime_id INTEGER NOT NULL REFERENCES public.regimes(regime_id) ON DELETE CASCADE,
    PRIMARY KEY (plat_id, regime_id)
);

CREATE TABLE public.plats_themes (
    plat_id INTEGER NOT NULL REFERENCES public.plats(plat_id) ON DELETE CASCADE,
    theme_id INTEGER NOT NULL REFERENCES public.themes(theme_id) ON DELETE CASCADE,
    PRIMARY KEY (plat_id, theme_id)
);