export interface Horaire {
  horaire_id: number;
  jour: string;
  heure_ouverture: string;
  heure_fermeture: string;
}

export interface AvisNotes {
  qualite: number;
  service: number;
  prix: number;
  moyenne: number;
}

export interface Avis {
  id: string;
  user_id: number;
  commande_id: number;
  client_nom?: string;
  notes: AvisNotes;
  description: string;
  statut: 'En attente' | 'Approuvé' | 'Rejeté';
  created_at: string;
}

export interface ContactCreate {
  nom: string;
  prenom: string;
  email: string;
  telephone?: string;
  objet: string;
  message: string;
  rgpd_consent: boolean;
}