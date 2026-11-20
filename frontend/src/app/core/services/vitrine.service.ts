import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { Avis, ContactCreate, Horaire } from '../models';

@Injectable({
  providedIn: 'root' // Disponible partout dans l'application (Singleton)
})
export class VitrineService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = environment.apiUrl;

  /** Récupère les horaires d'ouverture du restaurant traiteur (PostgreSQL) */
  getHoraires(): Observable<Horaire[]> {
    return this.http.get<Horaire[]>(`${this.apiUrl}/horaires`);
  }

  /** Récupère les avis clients approuvés (MongoDB) */
  getAvisApprouves(limit = 6): Observable<Avis[]> {
    const params = new HttpParams().set('limit', limit.toString());
    return this.http.get<Avis[]>(`${this.apiUrl}/avis`, { params });
  }

  /** Envoie un message de contact visiteur (MongoDB) */
  envoyerContact(payload: ContactCreate): Observable<unknown> {
    return this.http.post(`${this.apiUrl}/contact`, payload);
  }
}