import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { CurrencyPipe } from '@angular/common';
import { RouterLink } from '@angular/router';

import { BackofficeService } from '../../core/services/backoffice.service';
import { AdminStatsResponse, User, RefItem } from '../../core/models';
import { CatalogueService } from '../../core/services/catalogue.service'

const PASSWORD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{10,}$/;

const MOIS_LABELS: Record<number, string> = {
  1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril',
  5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août',
  9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
};

@Component({
  selector: 'app-admin-dashboard',
  imports: [ReactiveFormsModule, CurrencyPipe, RouterLink],
  templateUrl: './admin-dashboard.html',
  styleUrl: './admin-dashboard.scss'
})
export class AdminDashboard implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly backofficeService = inject(BackofficeService);
  private readonly catalogueService = inject(CatalogueService);

  ongletActif = signal<'stats' | 'equipe' | 'referentiels'>('stats');
  messageSucces = signal<string | null>(null);
  messageErreur = signal<string | null>(null);
  actionEnCours = signal(false);
  regimes = signal<RefItem[]>([]);
  themes = signal<RefItem[]>([]);

  // --- Données Statistiques MongoDB ---
  filtreAnnee = signal<number | undefined>(undefined);
  stats = signal<AdminStatsResponse | null>(null);
  chargementStats = signal(true);

  // Valeurs maximales calculées pour dimensionner proportionnellement les barres des graphiques
  maxMenuCa = computed(() => {
    const menus = this.stats()?.top_menus ?? [];
    return menus.length > 0 ? Math.max(...menus.map((m) => m.ca_genere_brut), 1) : 1;
  });

  maxMonthlyCa = computed(() => {
    const months = this.stats()?.evolution_mensuelle ?? [];
    return months.length > 0 ? Math.max(...months.map((m) => m.ca_ttc), 1) : 1;
  });

  // --- Données Gestion du Personnel ---
  employes = signal<User[]>([]);
  chargementEmployes = signal(true);

  employeeForm = this.fb.nonNullable.group({
    prenom: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(50)]],
    nom: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(50)]],
    email: ['', [Validators.required, Validators.email]],
    telephone: ['', [Validators.maxLength(20)]],
    password: ['', [Validators.required, Validators.pattern(PASSWORD_REGEX)]]
  });

  ngOnInit(): void {
    this.chargerStatistiques();
    this.chargerEmployes();
    this.chargerReferentiels();
  }

  // --- 1. Statistiques Analytiques NoSQL ---

  chargerStatistiques(): void {
    this.chargementStats.set(true);
    this.backofficeService.getAdminStats(this.filtreAnnee()).subscribe({
      next: (data) => {
        this.stats.set(data);
        this.chargementStats.set(false);
      },
      error: () => {
        this.chargementStats.set(false);
        this.messageErreur.set('Impossible de récupérer les agrégations analytiques MongoDB.');
      }
    });
  }

  changerAnneeStats(valeur: string): void {
    this.filtreAnnee.set(valeur ? Number(valeur) : undefined);
    this.chargerStatistiques();
  }

  formatMois(mois: number, annee: number): string {
    return `${MOIS_LABELS[mois] || 'Mois ' + mois} ${annee}`;
  }

  calculerPourcentage(valeur: number, maximum: number): number {
    if (!maximum || maximum <= 0) return 0;
    return Math.min(100, Math.round((valeur / maximum) * 100));
  }

  // --- 2. Gestion des Comptes Employés ---

  chargerEmployes(): void {
    this.chargementEmployes.set(true);
    this.backofficeService.getEmployees(true).subscribe({
      next: (data) => {
        this.employes.set(data);
        this.chargementEmployes.set(false);
      },
      error: () => {
        this.chargementEmployes.set(false);
        this.messageErreur.set('Erreur lors du chargement de la liste des collaborateurs.');
      }
    });
  }

  creerEmploye(): void {
    if (this.employeeForm.invalid) {
      this.employeeForm.markAllAsTouched();
      return;
    }

    this.resetMessages();
    this.actionEnCours.set(true);

    const raw = this.employeeForm.getRawValue();
    this.backofficeService.createEmployee({
      prenom: raw.prenom.trim(),
      nom: raw.nom.trim(),
      email: raw.email.trim(),
      telephone: raw.telephone.trim() || undefined,
      password: raw.password
    }).subscribe({
      next: (created) => {
        this.actionEnCours.set(false);
        this.employeeForm.reset();
        this.messageSucces.set(
          `Le compte collaborateur de ${created.prenom} ${created.nom} (${created.email}) a été créé avec le rôle Employé.`
        );
        this.chargerEmployes();
      },
      error: (err) => {
        this.actionEnCours.set(false);
        this.messageErreur.set(err?.error?.detail || 'Erreur lors de la création du compte employé.');
      }
    });
  }

  desactiverEmploye(emp: User): void {
    this.resetMessages();
    this.actionEnCours.set(true);

    this.backofficeService.disableEmployee(emp.user_id).subscribe({
      next: () => {
        this.actionEnCours.set(false);
        this.messageSucces.set(`Les accès de ${emp.prenom} ${emp.nom} ont été immédiatement révoqués.`);
        this.chargerEmployes();
      },
      error: (err) => {
        this.actionEnCours.set(false);
        this.messageErreur.set(err?.error?.detail || 'Impossible de désactiver ce compte.');
      }
    });
  }

  chargerReferentiels(): void {
  this.catalogueService.getFiltres().subscribe({
    next: (res) => {
      this.regimes.set(res.regimes);
      this.themes.set(res.themes);
    }
  });
  }

  ajouterRegime(libelle: string): void {
    const val = libelle.trim();
    if (!val) return;
    this.resetMessages();
    this.backofficeService.createRegime(val).subscribe({
      next: () => {
        this.messageSucces.set(`Régime « ${val} » ajouté.`);
        this.chargerReferentiels();
      },
      error: (err) => this.messageErreur.set(err?.error?.detail || 'Erreur ajout régime.')
    });
  }

  modifierRegime(id: number, libelle: string): void {
    const val = libelle.trim();
    if (!val) return;
    this.resetMessages();
    this.backofficeService.updateRegime(id, val).subscribe({
      next: () => {
        this.messageSucces.set(`Régime mis à jour en « ${val} ».`);
        this.chargerReferentiels();
      },
      error: (err) => this.messageErreur.set(err?.error?.detail || 'Erreur modification régime.')
    });
  }

  ajouterTheme(libelle: string): void {
    const val = libelle.trim();
    if (!val) return;
    this.resetMessages();
    this.backofficeService.createTheme(val).subscribe({
      next: () => {
        this.messageSucces.set(`Thème « ${val} » ajouté.`);
        this.chargerReferentiels();
      },
      error: (err) => this.messageErreur.set(err?.error?.detail || 'Erreur ajout thème.')
    });
  }

  modifierTheme(id: number, libelle: string): void {
    const val = libelle.trim();
    if (!val) return;
    this.resetMessages();
    this.backofficeService.updateTheme(id, val).subscribe({
      next: () => {
        this.messageSucces.set(`Thème mis à jour en « ${val} ».`);
        this.chargerReferentiels();
      },
      error: (err) => this.messageErreur.set(err?.error?.detail || 'Erreur modification thème.')
    });
  }

  private resetMessages(): void {
    this.messageSucces.set(null);
    this.messageErreur.set(null);
  }
}