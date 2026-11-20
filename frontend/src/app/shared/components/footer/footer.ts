import { Component, OnInit, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';

import { VitrineService } from '../../../core/services/vitrine.service';
import { Horaire } from '../../../core/models';

@Component({
  selector: 'app-footer',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './footer.html',
  styleUrl: './footer.scss'
})
export class Footer implements OnInit {
  private readonly vitrineService = inject(VitrineService);

  horaires = signal<Horaire[]>([]);
  chargementHoraires = signal(true);
  anneeCourante = new Date().getFullYear();

  ngOnInit(): void {
    this.vitrineService.getHoraires().subscribe({
      next: (data) => {
        this.horaires.set(data);
        this.chargementHoraires.set(false);
      },
      error: () => {
        // En cas d'indisponibilité API, on coupe simplement le chargement sans casser le rendu
        this.chargementHoraires.set(false);
      }
    });
  }
}