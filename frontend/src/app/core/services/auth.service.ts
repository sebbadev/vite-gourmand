import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable, catchError, of, switchMap, tap } from 'rxjs';

import { environment } from '../../../environments/environment';
import {
  ChangePasswordRequest,
  ForgotPasswordRequest,
  LoginRequest,
  MessageResponse,
  RegisterRequest,
  ResetPasswordRequest,
  TokenResponse,
  User,
  UserRole,
  UserUpdate
} from '../models';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  private readonly apiUrl = `${environment.apiUrl}/auth`;
  private readonly TOKEN_KEY = 'vg_access_token';

  // Source de vérité réactive de la session utilisateur
  private readonly currentUserSubject = new BehaviorSubject<User | null>(null);
  readonly currentUser$ = this.currentUserSubject.asObservable();

  constructor() {
    // Hydratation automatique au chargement de l'application si un jeton existe
    if (this.getToken()) {
      this.fetchCurrentUser().subscribe();
    }
  }

  /** Accès synchrone rapide à l'utilisateur courant */
  get currentUserValue(): User | null {
    return this.currentUserSubject.value;
  }

  get isAuthenticated(): boolean {
    return !!this.getToken() && !!this.currentUserSubject.value;
  }

  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  hasRole(allowedRoles: UserRole[]): boolean {
    const user = this.currentUserSubject.value;
    return !!user && allowedRoles.includes(user.role);
  }

  /** Inscription autonome (crée un compte Client puis connecte automatiquement) */
  register(payload: RegisterRequest): Observable<User> {
    return this.http.post<User>(`${this.apiUrl}/register`, payload);
  }

  /** Connexion : récupère le JWT, le stocke et hydrate le profil via /auth/me */
  login(credentials: LoginRequest): Observable<User | null> {
    return this.http.post<TokenResponse>(`${this.apiUrl}/login`, credentials).pipe(
      tap((res) => localStorage.setItem(this.TOKEN_KEY, res.access_token)),
      switchMap(() => this.fetchCurrentUser())
    );
  }

  /** Récupère le profil complet depuis GET /api/v1/auth/me */
  fetchCurrentUser(): Observable<User | null> {
    return this.http.get<User>(`${this.apiUrl}/me`).pipe(
      tap((user) => this.currentUserSubject.next(user)),
      catchError(() => {
        // Si le jeton est expiré ou invalide (401), on nettoie proprement la session
        this.clearSession();
        return of(null);
      })
    );
  }

  /** Mise à jour des coordonnées personnelles */
  updateProfile(payload: UserUpdate): Observable<User> {
    return this.http.patch<User>(`${this.apiUrl}/me`, payload).pipe(
      tap((updatedUser) => this.currentUserSubject.next(updatedUser))
    );
  }

  /** Changement de mot de passe depuis l'espace personnel */
  changePassword(payload: ChangePasswordRequest): Observable<MessageResponse> {
    return this.http.patch<MessageResponse>(`${this.apiUrl}/me/password`, payload);
  }

  /** Demande de réinitialisation de mot de passe */
  forgotPassword(payload: ForgotPasswordRequest): Observable<MessageResponse> {
    return this.http.post<MessageResponse>(`${this.apiUrl}/forgot-password`, payload);
  }

  /** Validation du jeton de réinitialisation */
  resetPassword(payload: ResetPasswordRequest): Observable<MessageResponse> {
    return this.http.post<MessageResponse>(`${this.apiUrl}/reset-password`, payload);
  }

  /** Déconnexion explicite */
  logout(): void {
    this.clearSession();
    this.router.navigate(['/connexion']);
  }

  private clearSession(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    this.currentUserSubject.next(null);
  }
}