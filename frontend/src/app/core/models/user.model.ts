export type UserRole = 'Visiteur' | 'Client' | 'Employe' | 'Admin';

export interface User {
  user_id: number;
  email: string;
  prenom: string;
  nom: string;
  telephone?: string | null;
  adresse?: string | null;
  code_postal?: string | null;
  ville?: string | null;
  pays?: string | null;
  role: UserRole;
  is_deleted: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}