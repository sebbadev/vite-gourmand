import { Component, OnInit, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { DatePipe, DecimalPipe } from '@angular/common';

import { VitrineService } from '../../core/services/vitrine.service';
import { Avis } from '../../core/models';

@Component({
  selector: 'app-home',
  imports: [RouterLink, DatePipe, DecimalPipe],
  templateUrl: './home.html',
  styleUrl: './home.scss'
})
export class Home implements OnInit {
  private readonly vitrineService = inject(VitrineService);

  avisList = signal<Avis[]>([]);
  chargementAvis = signal(true);

  ngOnInit(): void {
    this.vitrineService.getAvisApprouves(3).subscribe({
      next: (data) => {
        this.avisList.set(data);
        this.chargementAvis.set(false);
      },
      error: () => {
        this.chargementAvis.set(false);
      }
    });
  }
}