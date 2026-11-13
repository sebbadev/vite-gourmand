export type OrderStatus =
  | 'En attente de validation'
  | 'Acceptée'
  | 'Annulée'
  | 'En préparation'
  | 'En cours de livraison'
  | 'Livrée'
  | 'Terminée';

export type PaymentStatus = 'En attente de règlement' | 'Annulée' | 'Réglée';
export type EquipmentStatus = 'Inclus' | 'Non inclus' | 'Retourné';
export type ContactMode = 'Téléphone' | 'Email';

/** Élément stocké dans le panier local Angular */
export interface CartItem {
  menu_id: number;
  titre: string;
  prix_par_personne: number;
  nombre_personnes_min: number;
  quantite_disponible: number;
  images_url: string;
  quantite: number; // Nombre de convives choisis
}

export interface OrderItemCreate {
  menu_id: number;
  quantite: number;
}

export interface QuoteRequest {
  items: OrderItemCreate[];
  distance_km: number;
}

export interface QuoteResponse {
  sous_total_brut: number;
  remise_appliquee: number;
  sous_total_apres_remise: number;
  frais_livraison: number;
  prix_total: number;
  eligible_remise: boolean;
}

export interface OrderCreate {
  date_prestation: string;   // Format YYYY-MM-DD
  heure_livraison: string;   // Format HH:mm:ss
  adresse_livraison: string;
  distance_km: number;
  items: OrderItemCreate[];
}

export interface OrderUpdate {
  date_prestation?: string;
  heure_livraison?: string;
  adresse_livraison?: string;
  distance_km?: number;
  items?: OrderItemCreate[];
}

export interface OrderCancelRequest {
  motif_annulation: string;
  mode_contact_annulation?: ContactMode;
  contact_client_effectue?: boolean;
}

export interface OrderDetailRead {
  detail_id: number;
  menu_id: number;
  menu_titre?: string | null;
  quantite: number;
  prix_applique: number;
}

export interface OrderRead {
  commande_id: number;
  numero_commande: string;
  user_id: number;
  date_prestation: string;
  heure_livraison: string;
  adresse_livraison?: string | null;
  distance_km: number;
  frais_livraison: number;
  remise_appliquee: number;
  prix_total: number;
  statut: OrderStatus;
  statut_paiement: PaymentStatus;
  statut_materiel: EquipmentStatus;
  date_commande?: string | null;
  motif_annulation?: string | null;
  mode_contact_annulation?: ContactMode | null;
  contact_client_effectue: boolean;
  created_at?: string | null;
  details: OrderDetailRead[];
}

export interface AvisCreate {
  qualite: number;     // 1 à 5
  service: number;     // 1 à 5
  prix: number;        // 1 à 5
  description: string;
}