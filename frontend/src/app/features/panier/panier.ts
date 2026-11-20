import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { CurrencyPipe, DatePipe } from '@angular/common';
import { combineLatest, debounceTime, of, startWith, switchMap } from 'rxjs';

import { CartService } from '../../core/services/cart.service';
import { OrderService } from '../../core/services/order.service';
import { AuthService } from '../../core/services/auth.service';
import { CartItem, OrderCreate, OrderRead, QuoteResponse } from '../../core/models';

@Component({
  selector: 'app-panier',
  imports: [ReactiveFormsModule, RouterLink, CurrencyPipe, DatePipe],
  templateUrl: './panier.html',
  styleUrl: './panier.scss'
})
export class PanierPage implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly cartService = inject(CartService);
  private readonly orderService = inject(OrderService);
  readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  items = signal<CartItem[]>([]);
  devis = signal<QuoteResponse | null>(null);
  commandeConfirmee = signal<OrderRead | null>(null);
  calculEnCours = signal(false);
  validationEnCours = signal(false);
  erreurMessage = signal<string | null>(null);

  readonly minDatePrestation = new Date(Date.now() + 86_400_000).toISOString().split('T')[0];

  deliveryForm = this.fb.nonNullable.group({
    date_prestation: [this.minDatePrestation, [Validators.required]],
    heure_livraison: ['12:30', [Validators.required]],
    adresse_livraison: ['', [Validators.required, Validators.minLength(5), Validators.maxLength(255)]],
    distance_km: [0, [Validators.required, Validators.min(0)]]
  });

  ngOnInit(): void {
    // 1. Restaurer le brouillon de livraison s'il existe, sinon pré-remplir depuis le profil
    const draft = this.cartService.getDeliveryDraft();
    const user = this.authService.currentUserValue;

    if (draft) {
      this.deliveryForm.patchValue(draft);
    } else if (user?.adresse) {
      const adresseComplete = [user.adresse, user.code_postal, user.ville].filter(Boolean).join(', ');
      this.deliveryForm.patchValue({ adresse_livraison: adresseComplete });
    }

    // 2. Sauvegarder chaque modification du formulaire de livraison en temps réel
    this.deliveryForm.valueChanges.subscribe(() => {
      this.cartService.saveDeliveryDraft(this.deliveryForm.getRawValue());
    });

    // 3. Recalculer le devis API dès que le panier ou la distance change
    const distance$ = this.deliveryForm.controls.distance_km.valueChanges.pipe(
      startWith(this.deliveryForm.controls.distance_km.value)
    );

    combineLatest([this.cartService.items$, distance$]).pipe(
      debounceTime(250),
      switchMap(([cartItems, distanceKm]) => {
        this.items.set(cartItems);
        if (cartItems.length === 0) {
          this.devis.set(null);
          return of(null);
        }

        this.calculEnCours.set(true);
        return this.orderService.simulerDevis({
          items: cartItems.map((i) => ({ menu_id: i.menu_id, quantite: i.quantite })),
          distance_km: Number(distanceKm) || 0
        });
      })
    ).subscribe({
      next: (quote) => {
        this.devis.set(quote);
        this.calculEnCours.set(false);
      },
      error: (err) => {
        this.calculEnCours.set(false);
        this.erreurMessage.set(err?.error?.detail || 'Erreur lors du calcul du devis.');
      }
    });
  }

  modifierQuantite(menuId: number, nouvelleQte: string): void {
    const val = Number(nouvelleQte);
    if (!Number.isNaN(val) && val > 0) {
      this.cartService.updateQuantity(menuId, val);
    }
  }

  retirerMenu(menuId: number): void {
    this.cartService.removeItem(menuId);
  }

  validerCommande(): void {
    if (!this.authService.isAuthenticated) {
      this.router.navigate(['/connexion'], { queryParams: { returnUrl: '/panier' } });
      return;
    }

    if (this.items().length === 0 || this.deliveryForm.invalid) {
      this.deliveryForm.markAllAsTouched();
      return;
    }

    this.validationEnCours.set(true);
    this.erreurMessage.set(null);

    const formVal = this.deliveryForm.getRawValue();
    const heureFormatee = formVal.heure_livraison.length === 5
      ? `${formVal.heure_livraison}:00`
      : formVal.heure_livraison;

    const payload: OrderCreate = {
      date_prestation: formVal.date_prestation,
      heure_livraison: heureFormatee,
      adresse_livraison: formVal.adresse_livraison.trim(),
      distance_km: Number(formVal.distance_km) || 0,
      items: this.items().map((i) => ({ menu_id: i.menu_id, quantite: i.quantite }))
    };

    this.orderService.creerCommande(payload).subscribe({
      next: (order) => {
        this.validationEnCours.set(false);
        this.cartService.clearCart();
        this.commandeConfirmee.set(order);
      },
      error: (err) => {
        this.validationEnCours.set(false);
        this.erreurMessage.set(err?.error?.detail || 'Impossible d’enregistrer votre commande.');
      }
    });
  }
}