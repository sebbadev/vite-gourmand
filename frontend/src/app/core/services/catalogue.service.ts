import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { CatalogueFilters, MenuDetail, MenuListItem } from '../models';

export interface MenuQueryFilters {
  prix_max?: number | null;
  nb_personnes?: number | null;
  theme_id?: number | null;
  regime_id?: number | null;
  sans_allergene_id?: number | null;
}

@Injectable({
  providedIn: 'root'
})
export class CatalogueService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/menus`;

  /** Récupère les listes de référence (thèmes, régimes, allergènes) pour les menus déroulants */
  getFiltres(): Observable<CatalogueFilters> {
    return this.http.get<CatalogueFilters>(`${this.apiUrl}/filtres`);
  }

  /** Récupère les menus actifs selon les filtres combinés sélectionnés */
  getMenus(filters?: MenuQueryFilters): Observable<MenuListItem[]> {
    let params = new HttpParams();

    if (filters) {
      if (filters.prix_max != null && filters.prix_max > 0) {
        params = params.set('prix_max', filters.prix_max.toString());
      }
      if (filters.nb_personnes != null && filters.nb_personnes > 0) {
        params = params.set('nb_personnes', filters.nb_personnes.toString());
      }
      if (filters.theme_id != null) {
        params = params.set('theme_id', filters.theme_id.toString());
      }
      if (filters.regime_id != null) {
        params = params.set('regime_id', filters.regime_id.toString());
      }
      if (filters.sans_allergene_id != null) {
        params = params.set('sans_allergene_id', filters.sans_allergene_id.toString());
      }
    }

    return this.http.get<MenuListItem[]>(this.apiUrl, { params });
  }

  /** Récupère la fiche détaillée d'un menu (plats associés, badges régimes/allergènes) */
  getMenuById(menuId: number): Observable<MenuDetail> {
    return this.http.get<MenuDetail>(`${this.apiUrl}/${menuId}`);
  }
}