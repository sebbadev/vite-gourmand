import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import {
  AdminStatsResponse,
  Avis,
  AvisModerationUpdate,
  ContactRead,
  EmployeeCreatePayload,
  Horaire,
  HoraireUpdatePayload,
  MenuCreatePayload,
  MenuDetail,
  OrderCancelRequest,
  OrderRead,
  OrderStatusUpdate,
  Plat,
  PlatCreatePayload,
  RefItem,
  User
} from '../models';

@Injectable({
  providedIn: 'root'
})
export class BackofficeService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = environment.apiUrl;

  // --- 1. Gestion des Commandes (Employé / Admin) ---

  getToutesCommandes(activesUniquement = false, statut?: string): Observable<OrderRead[]> {
    let params = new HttpParams().set('actives_uniquement', activesUniquement.toString());
    if (statut) {
      params = params.set('statut', statut);
    }
    return this.http.get<OrderRead[]>(`${this.apiUrl}/commandes/admin/toutes`, { params });
  }

  updateStatutCommande(commandeId: number, payload: OrderStatusUpdate): Observable<OrderRead> {
    return this.http.patch<OrderRead>(`${this.apiUrl}/commandes/${commandeId}/statut`, payload);
  }

  annulerCommandeEmploye(commandeId: number, payload: OrderCancelRequest): Observable<OrderRead> {
    return this.http.post<OrderRead>(`${this.apiUrl}/commandes/${commandeId}/annuler`, payload);
  }

  // --- 2. Gestion du Catalogue : Menus & Plats (Employé / Admin) ---

  getPlats(): Observable<Plat[]> {
    return this.http.get<Plat[]>(`${this.apiUrl}/plats`);
  }

  createPlat(payload: PlatCreatePayload): Observable<Plat> {
    return this.http.post<Plat>(`${this.apiUrl}/plats`, payload);
  }

  updatePlat(platId: number, payload: Partial<PlatCreatePayload>): Observable<Plat> {
    return this.http.put<Plat>(`${this.apiUrl}/plats/${platId}`, payload);
  }
  
  deletePlat(platId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/plats/${platId}`);
  }

  createMenu(payload: MenuCreatePayload): Observable<MenuDetail> {
    return this.http.post<MenuDetail>(`${this.apiUrl}/menus`, payload);
  }

  updateMenu(menuId: number, payload: Partial<MenuCreatePayload>): Observable<MenuDetail> {
    return this.http.put<MenuDetail>(`${this.apiUrl}/menus/${menuId}`, payload);
  }

  deleteMenu(menuId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/menus/${menuId}`);
  }

  // --- 3. Modération des Avis MongoDB (Employé / Admin) ---

  getAvisAdmin(statut?: string): Observable<Avis[]> {
    let params = new HttpParams();
    if (statut) {
      params = params.set('statut', statut);
    }
    return this.http.get<Avis[]>(`${this.apiUrl}/admin/avis`, { params });
  }

  modererAvis(avisId: string, payload: AvisModerationUpdate): Observable<Avis> {
    return this.http.patch<Avis>(`${this.apiUrl}/admin/avis/${avisId}`, payload);
  }

  // --- 4. Messages de Contact & Horaires (Employé / Admin) ---

  getContactsAdmin(): Observable<ContactRead[]> {
    return this.http.get<ContactRead[]>(`${this.apiUrl}/admin/contacts`);
  }

  marquerContactTraite(contactId: string): Observable<ContactRead> {
    return this.http.patch<ContactRead>(`${this.apiUrl}/admin/contacts/${contactId}/traite`, {});
  }

  updateHoraire(horaireId: number, payload: HoraireUpdatePayload): Observable<Horaire> {
    return this.http.put<Horaire>(`${this.apiUrl}/horaires/${horaireId}`, payload);
  }

  // --- 5. Direction : Personnel & Statistiques NoSQL (Admin uniquement) ---

  getEmployees(includeDisabled = true): Observable<User[]> {
    const params = new HttpParams().set('include_disabled', includeDisabled.toString());
    return this.http.get<User[]>(`${this.apiUrl}/admin/employees`, { params });
  }

  createEmployee(payload: EmployeeCreatePayload): Observable<User> {
    return this.http.post<User>(`${this.apiUrl}/admin/employees`, payload);
  }

  disableEmployee(userId: number): Observable<User> {
    return this.http.patch<User>(`${this.apiUrl}/admin/employees/${userId}/disable`, {});
  }

  getAdminStats(annee?: number): Observable<AdminStatsResponse> {
    let params = new HttpParams();
    if (annee) {
      params = params.set('annee', annee.toString());
    }
    return this.http.get<AdminStatsResponse>(`${this.apiUrl}/admin/stats`, { params });
  }

  // --- 6. Référentiels : Régimes & Thèmes (Admin uniquement) ---

  createRegime(libelle: string): Observable<RefItem> {
    return this.http.post<RefItem>(`${this.apiUrl}/admin/referentiels/regimes`, { libelle });
  }

  updateRegime(regimeId: number, libelle: string): Observable<RefItem> {
    return this.http.put<RefItem>(`${this.apiUrl}/admin/referentiels/regimes/${regimeId}`, { libelle });
  }

  createTheme(libelle: string): Observable<RefItem> {
    return this.http.post<RefItem>(`${this.apiUrl}/admin/referentiels/themes`, { libelle });
  }

  updateTheme(themeId: number, libelle: string): Observable<RefItem> {
    return this.http.put<RefItem>(`${this.apiUrl}/admin/referentiels/themes/${themeId}`, { libelle });
  }
}