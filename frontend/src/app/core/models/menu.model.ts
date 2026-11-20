export type DishType = 'Entrée' | 'Plat principal' | 'Accompagnement' | 'Dessert';

export interface RefItem {
  id: number;
  libelle: string;
}

export interface Plat {
  plat_id: number;
  titre: string;
  type_de_plat: DishType;
  images_url?: string | null;
  allergenes: RefItem[];
  regimes: RefItem[];
  themes: RefItem[];
}

export interface MenuListItem {
  menu_id: number;
  titre: string;
  nombre_personnes_min: number;
  prix_par_personne: number;
  description: string;
  quantite_disponible: number;
  images_url: string;
  is_active: boolean;
  themes: RefItem[];
  regimes: RefItem[];
  allergenes: RefItem[];
}

export interface MenuDetail extends MenuListItem {
  created_at?: string;
  updated_at?: string;
  plats: Plat[];
}

export interface CatalogueFilters {
  themes: RefItem[];
  regimes: RefItem[];
  allergenes: RefItem[];
}