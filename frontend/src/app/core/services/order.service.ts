import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import {
  AvisCreate,
  OrderCancelRequest,
  OrderCreate,
  OrderRead,
  OrderUpdate,
  QuoteRequest,
  QuoteResponse
} from '../models';

@Injectable({
  providedIn: 'root'
})
export class OrderService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/commandes`;

  /** Simule le calcul de devis côté backend (RG-01, RG-02, RG-03) */
  simulerDevis(payload: QuoteRequest): Observable<QuoteResponse> {
    return this.http.post<QuoteResponse>(`${this.apiUrl}/devis`, payload);
  }

  /** Crée une commande ferme (Client authentifié) */
  creerCommande(payload: OrderCreate): Observable<OrderRead> {
    return this.http.post<OrderRead>(this.apiUrl, payload);
  }

  /** Récupère l'historique personnel des commandes du client connecté */
  getMesCommandes(): Observable<OrderRead[]> {
    return this.http.get<OrderRead[]>(`${this.apiUrl}/me`);
  }

  /** Modifie la date, l'heure, l'adresse ou les quantités avant acceptation */
  modifierCommande(commandeId: number, payload: OrderUpdate): Observable<OrderRead> {
    return this.http.patch<OrderRead>(`${this.apiUrl}/${commandeId}`, payload);
  }

  /** Annule une commande (par le client avant acceptation, ou par l'équipe) */
  annulerCommande(commandeId: number, payload: OrderCancelRequest): Observable<OrderRead> {
    return this.http.post<OrderRead>(`${this.apiUrl}/${commandeId}/annuler`, payload);
  }

  /** Dépose un avis multicritère sur une commande au statut 'Terminée' */
  deposerAvis(commandeId: number, payload: AvisCreate): Observable<unknown> {
    return this.http.post(`${this.apiUrl}/${commandeId}/avis`, payload);
  }
}