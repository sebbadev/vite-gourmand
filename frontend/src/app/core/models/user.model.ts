export type UserRole = 'Visiteur' | 'Client' | 'Employé' | 'Administrateur';

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

export interface RegisterRequest {
  email: string;
  password: string;
  prenom: string;
  nom: string;
  telephone?: string;
  adresse?: string;
  code_postal?: string;
  ville?: string;
  pays?: string;
}

export interface UserUpdate {
  prenom?: string;
  nom?: string;
  telephone?: string;
  adresse?: string;
  code_postal?: string;
  ville?: string;
  pays?: string;
}

export interface ChangePasswordRequest {
  ancien_password: string;
  nouveau_password: string;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  nouveau_password: string;
}

export interface MessageResponse {
  message: string;
}