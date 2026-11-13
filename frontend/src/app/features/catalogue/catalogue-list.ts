import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { CurrencyPipe } from '@angular/common';
import { debounceTime, distinctUntilChanged, startWith, switchMap } from 'rxjs';

import { CatalogueService, MenuQueryFilters } from '../../core/services/catalogue.service';
import { CatalogueFilters, MenuListItem } from '../../core/models';

@Component({
  selector: 'app-catalogue-list',
  imports: [ReactiveFormsModule, RouterLink, CurrencyPipe],
  templateUrl: './catalogue-list.html',
  styleUrl: './catalogue-list.scss'
})
export class CatalogueList implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly catalogueService = inject(CatalogueService);

  menus = signal<MenuListItem[]>([]);
  referentiels = signal<CatalogueFilters>({ themes: [], regimes: [], allergenes: [] });
  chargement = signal(true);
  erreurMessage = signal<string | null>(null);

  filterForm = this.fb.group({
    prix_max: [null as number | null],
    nb_personnes: [null as number | null],
    theme_id: [null as number | null],
    regime_id: [null as number | null],
    sans_allergene_id: [null as number | null]
  });

  ngOnInit(): void {
    // 1. Chargement des listes déroulantes (thèmes, régimes, allergènes)
    this.catalogueService.getFiltres().subscribe({
      next: (data) => this.referentiels.set(data)
    });

    // 2. Écoute réactive des changements de filtres
    this.filterForm.valueChanges.pipe(
      startWith(this.filterForm.value),
      debounceTime(300),
      distinctUntilChanged((prev, curr) => JSON.stringify(prev) === JSON.stringify(curr)),
      switchMap((valeurs) => {
        this.chargement.set(true);
        this.erreurMessage.set(null);
        return this.catalogueService.getMenus(valeurs as MenuQueryFilters);
      })
    ).subscribe({
      next: (data) => {
        this.menus.set(data);
        this.chargement.set(false);
      },
      error: () => {
        this.chargement.set(false);
        this.erreurMessage.set('Impossible de charger le catalogue des menus.');
      }
    });
  }

  reinitialiserFiltres(): void {
    this.filterForm.reset({
      prix_max: null,
      nb_personnes: null,
      theme_id: null,
      regime_id: null,
      sans_allergene_id: null
    });
  }
}