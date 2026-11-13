import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { CurrencyPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { CatalogueService } from '../../core/services/catalogue.service';
import { AuthService } from '../../core/services/auth.service';
import { MenuDetail } from '../../core/models';
import { CartService } from '../../core/services/cart.service';

export interface GalleryPhoto {
  url: string;
  label: string;
}

@Component({
  selector: 'app-menu-detail',
  imports: [RouterLink, CurrencyPipe, FormsModule],
  templateUrl: './menu-detail.html',
  styleUrl: './menu-detail.scss'
})
export class MenuDetailPage implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly catalogueService = inject(CatalogueService);
  private readonly authService = inject(AuthService);
  private readonly cartService = inject(CartService);
  
  menu = signal<MenuDetail | null>(null);
  chargement = signal(true);
  erreurMessage = signal<string | null>(null);
  nbConvives = signal(1);
  selectedPhotoUrl = signal<string | null>(null);

  // Image de secours SVG inline (zéro dépendance externe, jamais cassée)
  readonly fallbackImage =
    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='800' height='500' viewBox='0 0 800 500'><rect width='800' height='500' fill='%236b2737'/><text x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' fill='%23faf8f5' font-family='Georgia, serif' font-size='28'>Vite %26 Gourmand — Traiteur</text></svg>";

  // Construit automatiquement la galerie : photo du menu + photo de chaque plat associé
  galeriePhotos = computed<GalleryPhoto[]>(() => {
    const m = this.menu();
    if (!m) return [];

    const photos: GalleryPhoto[] = [
      { url: m.images_url, label: `Vue d'ensemble — ${m.titre}` }
    ];

    for (const plat of m.plats) {
      if (plat.images_url) {
        photos.push({
          url: plat.images_url,
          label: `${plat.type_de_plat} : ${plat.titre}`
        });
      }
    }
    return photos;
  });

  ngOnInit(): void {
    const idParam = this.route.snapshot.paramMap.get('id');
    const menuId = Number(idParam);

    if (!menuId || Number.isNaN(menuId)) {
      this.chargement.set(false);
      this.erreurMessage.set('Identifiant de menu invalide.');
      return;
    }

    this.catalogueService.getMenuById(menuId).subscribe({
      next: (data) => {
        this.menu.set(data);
        this.nbConvives.set(data.nombre_personnes_min);
        this.selectedPhotoUrl.set(data.images_url);
        this.chargement.set(false);
      },
      error: () => {
        this.chargement.set(false);
        this.erreurMessage.set('Menu introuvable ou indisponible.');
      }
    });
  }

  choisirPhoto(url: string): void {
    this.selectedPhotoUrl.set(url);
  }

  onImageError(event: Event): void {
    const img = event.target as HTMLImageElement;
    if (img.src !== this.fallbackImage) {
      img.src = this.fallbackImage;
    }
  }

  commanderMenu(): void {
    const currentMenu = this.menu();
    if (!currentMenu) return;

    const quantiteValide = Math.max(this.nbConvives(), currentMenu.nombre_personnes_min);
    this.cartService.addOrUpdateMenu(currentMenu, quantiteValide);

    if (!this.authService.isAuthenticated) {
      this.router.navigate(['/connexion'], {
        queryParams: { returnUrl: '/panier' }
      });
      return;
    }

    this.router.navigate(['/panier']);
  }
}