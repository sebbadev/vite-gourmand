import { Component, inject, signal } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { AsyncPipe } from '@angular/common';

import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-header',
  imports: [RouterLink, RouterLinkActive, AsyncPipe],
  templateUrl: './header.html',
  styleUrl: './header.scss'
})
export class Header {
  private readonly authService = inject(AuthService);

  // Flux réactif exposé directement au gabarit HTML
  readonly currentUser$ = this.authService.currentUser$;

  menuOuvert = signal(false);

  toggleMenu(): void {
    this.menuOuvert.update((etat) => !etat);
  }

  fermerMenu(): void {
    this.menuOuvert.set(false);
  }

  seDeconnecter(): void {
    this.fermerMenu();
    this.authService.logout();
  }
}