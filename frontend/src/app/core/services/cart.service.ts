import { Injectable } from '@angular/core';
import { BehaviorSubject, map } from 'rxjs';

import { CartItem, MenuDetail, MenuListItem } from '../models';

export interface DeliveryDraft {
  date_prestation: string;
  heure_livraison: string;
  adresse_livraison: string;
  distance_km: number;
}

@Injectable({
  providedIn: 'root'
})
export class CartService {
  private readonly CART_KEY = 'vg_cart_items';
  private readonly DELIVERY_KEY = 'vg_delivery_draft';

  private readonly itemsSubject = new BehaviorSubject<CartItem[]>(this.loadFromStorage());
  readonly items$ = this.itemsSubject.asObservable();

  /** Nombre total de menus distincts dans le panier (pour le badge du Header) */
  readonly count$ = this.items$.pipe(map((items) => items.length));

  get currentItems(): CartItem[] {
    return this.itemsSubject.value;
  }

  /** Sauvegarde les informations de livraison saisies pendant la navigation */
  saveDeliveryDraft(draft: DeliveryDraft): void {
    localStorage.setItem(this.DELIVERY_KEY, JSON.stringify(draft));
  }

  /** Relit les informations de livraison précédemment saisies */
  getDeliveryDraft(): DeliveryDraft | null {
    try {
      const raw = localStorage.getItem(this.DELIVERY_KEY);
      return raw ? (JSON.parse(raw) as DeliveryDraft) : null;
    } catch {
      return null;
    }
  }

  /** Ajoute un menu ou met à jour son nombre de convives (en respectant le seuil minimum) */
  addOrUpdateMenu(menu: MenuListItem | MenuDetail, quantite: number): void {
    const qtyValide = Math.max(quantite, menu.nombre_personnes_min);
    const items = [...this.itemsSubject.value];
    const index = items.findIndex((i) => i.menu_id === menu.menu_id);

    const newItem: CartItem = {
      menu_id: menu.menu_id,
      titre: menu.titre,
      prix_par_personne: menu.prix_par_personne,
      nombre_personnes_min: menu.nombre_personnes_min,
      quantite_disponible: menu.quantite_disponible,
      images_url: menu.images_url,
      quantite: qtyValide
    };

    if (index >= 0) {
      items[index] = newItem;
    } else {
      items.push(newItem);
    }

    this.saveAndEmit(items);
  }

  /** Modifie directement le nombre de convives d'une ligne du panier */
  updateQuantity(menuId: number, quantite: number): void {
    const items = this.itemsSubject.value.map((item) => {
      if (item.menu_id !== menuId) return item;
      const qtyValide = Math.max(quantite, item.nombre_personnes_min);
      return { ...item, quantite: qtyValide };
    });
    this.saveAndEmit(items);
  }

  /** Supprime un menu du panier */
  removeItem(menuId: number): void {
    const filtered = this.itemsSubject.value.filter((item) => item.menu_id !== menuId);
    this.saveAndEmit(filtered);
  }

  /** Vide intégralement le panier et le brouillon de livraison après validation */
  clearCart(): void {
    localStorage.removeItem(this.DELIVERY_KEY);
    this.saveAndEmit([]);
  }

  private saveAndEmit(items: CartItem[]): void {
    localStorage.setItem(this.CART_KEY, JSON.stringify(items));
    this.itemsSubject.next(items);
  }

  private loadFromStorage(): CartItem[] {
    try {
      const raw = localStorage.getItem(this.CART_KEY);
      return raw ? (JSON.parse(raw) as CartItem[]) : [];
    } catch {
      return [];
    }
  }
}