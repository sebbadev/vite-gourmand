import { Component, signal } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './header.html',
  styleUrl: './header.scss'
})
export class Header {
  // État réactif du menu mobile (burger)
  menuOuvert = signal(false);

  toggleMenu(): void {
    this.menuOuvert.update((etat) => !etat);
  }

  fermerMenu(): void {
    this.menuOuvert.set(false);
  }
}