import { ContactMode, EquipmentStatus, OrderStatus, PaymentStatus } from './order.model';
import { DishType } from './menu.model'

export interface OrderStatusUpdate {
  nouveau_statut?: OrderStatus;
  statut_paiement?: PaymentStatus;
  statut_materiel?: EquipmentStatus;
}

export interface MenuCreatePayload {
  titre: string;
  nombre_personnes_min: number;
  prix_par_personne: number;
  description: string;
  quantite_disponible: number;
  images_url: string;
  is_active: boolean;
  plat_ids: number[];
  theme_ids: number[];
}

export interface PlatCreatePayload {
  titre: string;
  type_de_plat: DishType;
  images_url?: string | null;
  allergene_ids: number[];
  regime_ids: number[];
  theme_ids: number[];
}

export interface HoraireUpdatePayload {
  heure_ouverture: string; // Format HH:mm:ss
  heure_fermeture: string; // Format HH:mm:ss
}

export interface ContactRead {
  id: string;
  nom: string;
  prenom: string;
  email: string;
  telephone?: string | null;
  objet: string;
  message: string;
  traite: boolean;
  created_at: string;
}

export interface AvisModerationUpdate {
  statut: 'En attente' | 'Approuvé' | 'Rejeté';
}

export interface GlobalKPIs {
  nombre_commandes: number;
  ca_ht: number;
  tva_collectee: number;
  ca_ttc: number;
  panier_moyen_ttc: number;
  total_remises: number;
  total_frais_livraison: number;
}

export interface TopMenuStat {
  menu_id: number;
  titre: string;
  portions_vendues: number;
  ca_genere_brut: number;
}

export interface MonthlyRevenueStat {
  annee: number;
  mois: number;
  nombre_commandes: number;
  ca_ht: number;
  ca_ttc: number;
}

export interface AdminStatsResponse {
  filtre_annee?: number | null;
  kpis_globaux: GlobalKPIs;
  top_menus: TopMenuStat[];
  evolution_mensuelle: MonthlyRevenueStat[];
}

export interface EmployeeCreatePayload {
  email: string;
  password: string;
  prenom: string;
  nom: string;
  telephone?: string;
}

export type { ContactMode };