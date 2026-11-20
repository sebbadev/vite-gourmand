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
}

export interface Avis {
  id: string;
  commande_id: number;
  numero_commande?: string | null;
  user_id: number;
  auteur_prenom?: string | null;
  notes: AvisNotes;
  note_moyenne: number;
  description: string;
  statut: 'En attente' | 'Approuvé' | 'Répondu' | 'Rejeté';
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