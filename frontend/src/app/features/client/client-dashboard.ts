import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { CurrencyPipe, DatePipe } from '@angular/common';

import { AuthService } from '../../core/services/auth.service';
import { OrderService } from '../../core/services/order.service';
import { OrderRead } from '../../core/models';

const PASSWORD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{10,}$/;

@Component({
  selector: 'app-client-dashboard',
  imports: [ReactiveFormsModule, RouterLink, CurrencyPipe, DatePipe],
  templateUrl: './client-dashboard.html',
  styleUrl: './client-dashboard.scss'
})
export class ClientDashboard implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly route = inject(ActivatedRoute);
  readonly authService = inject(AuthService);
  private readonly orderService = inject(OrderService);

  // Onglet actif : 'commandes' | 'profil'
  ongletActif = signal<'commandes' | 'profil'>('commandes');

  commandes = signal<OrderRead[]>([]);
  chargementCommandes = signal(true);
  messageGlobal = signal<string | null>(null);
  erreurGlobale = signal<string | null>(null);

  // Identifiants des modales / panneaux dépliables par commande
  commandeEnEditionId = signal<number | null>(null);
  commandeEnAnnulationId = signal<number | null>(null);
  commandeEnAvisId = signal<number | null>(null);
  actionEnCours = signal(false);

  // Formulaire de modification logistique avant acceptation
  editOrderForm = this.fb.nonNullable.group({
    date_prestation: ['', [Validators.required]],
    heure_livraison: ['', [Validators.required]],
    adresse_livraison: ['', [Validators.required, Validators.minLength(5), Validators.maxLength(255)]]
  });

  // Formulaire d'annulation autonome client
  cancelOrderForm = this.fb.nonNullable.group({
    motif_annulation: ['', [Validators.required, Validators.minLength(5), Validators.maxLength(255)]]
  });

  // Formulaire de dépôt d'avis multicritère (1 à 5)
  avisForm = this.fb.nonNullable.group({
    qualite: [5, [Validators.required, Validators.min(1), Validators.max(5)]],
    service: [5, [Validators.required, Validators.min(1), Validators.max(5)]],
    prix: [5, [Validators.required, Validators.min(1), Validators.max(5)]],
    description: ['', [Validators.required, Validators.minLength(10), Validators.maxLength(1000)]]
  });

  // Formulaire de mise à jour des coordonnées personnelles
  profilForm = this.fb.nonNullable.group({
    prenom: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(50)]],
    nom: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(50)]],
    telephone: ['', [Validators.maxLength(20)]],
    adresse: ['', [Validators.maxLength(255)]],
    code_postal: ['', [Validators.maxLength(10)]],
    ville: ['', [Validators.maxLength(50)]]
  });

  // Formulaire de changement de mot de passe
  passwordForm = this.fb.nonNullable.group({
    ancien_password: ['', [Validators.required]],
    nouveau_password: ['', [Validators.required, Validators.pattern(PASSWORD_REGEX)]]
  });

  ngOnInit(): void {
    if (this.route.snapshot.queryParamMap.get('commandeCreee') === '1') {
      this.messageGlobal.set('Votre commande a bien été enregistrée et transmise à notre équipe.');
    }

    this.chargerCommandes();
    this.initialiserProfil();
  }

  chargerCommandes(): void {
    this.chargementCommandes.set(true);
    this.orderService.getMesCommandes().subscribe({
      next: (data) => {
        this.commandes.set(data);
        this.chargementCommandes.set(false);
      },
      error: () => {
        this.chargementCommandes.set(false);
        this.erreurGlobale.set('Impossible de charger votre historique de commandes.');
      }
    });
  }

  private initialiserProfil(): void {
    const user = this.authService.currentUserValue;
    if (user) {
      this.profilForm.patchValue({
        prenom: user.prenom,
        nom: user.nom,
        telephone: user.telephone ?? '',
        adresse: user.adresse ?? '',
        code_postal: user.code_postal ?? '',
        ville: user.ville ?? ''
      });
    }
  }

  // --- Actions sur les commandes ---

  ouvrirEdition(cmd: OrderRead): void {
    this.fermerPanneauxCommande();
    this.commandeEnEditionId.set(cmd.commande_id);
    this.editOrderForm.patchValue({
      date_prestation: cmd.date_prestation,
      heure_livraison: cmd.heure_livraison.slice(0, 5),
      adresse_livraison: cmd.adresse_livraison ?? ''
    });
  }

  soumettreEdition(commandeId: number): void {
    if (this.editOrderForm.invalid) {
      this.editOrderForm.markAllAsTouched();
      return;
    }

    this.actionEnCours.set(true);
    this.resetMessages();

    const raw = this.editOrderForm.getRawValue();
    const heureFormatee = raw.heure_livraison.length === 5 ? `${raw.heure_livraison}:00` : raw.heure_livraison;

    this.orderService.modifierCommande(commandeId, {
      date_prestation: raw.date_prestation,
      heure_livraison: heureFormatee,
      adresse_livraison: raw.adresse_livraison.trim()
    }).subscribe({
      next: () => {
        this.actionEnCours.set(false);
        this.fermerPanneauxCommande();
        this.messageGlobal.set('Les informations de votre commande ont été mises à jour.');
        this.chargerCommandes();
      },
      error: (err) => {
        this.actionEnCours.set(false);
        this.erreurGlobale.set(err?.error?.detail || 'Modification impossible.');
      }
    });
  }

  ouvrirAnnulation(commandeId: number): void {
    this.fermerPanneauxCommande();
    this.commandeEnAnnulationId.set(commandeId);
    this.cancelOrderForm.reset();
  }

  soumettreAnnulation(commandeId: number): void {
    if (this.cancelOrderForm.invalid) {
      this.cancelOrderForm.markAllAsTouched();
      return;
    }

    this.actionEnCours.set(true);
    this.resetMessages();

    this.orderService.annulerCommande(commandeId, {
      motif_annulation: this.cancelOrderForm.controls.motif_annulation.value.trim()
    }).subscribe({
      next: () => {
        this.actionEnCours.set(false);
        this.fermerPanneauxCommande();
        this.messageGlobal.set('Votre commande a été annulée et les stocks ont été libérés.');
        this.chargerCommandes();
      },
      error: (err) => {
        this.actionEnCours.set(false);
        this.erreurGlobale.set(err?.error?.detail || 'Annulation impossible.');
      }
    });
  }

  ouvrirAvis(commandeId: number): void {
    this.fermerPanneauxCommande();
    this.commandeEnAvisId.set(commandeId);
    this.avisForm.reset({ qualite: 5, service: 5, prix: 5, description: '' });
  }

  soumettreAvis(commandeId: number): void {
    if (this.avisForm.invalid) {
      this.avisForm.markAllAsTouched();
      return;
    }

    this.actionEnCours.set(true);
    this.resetMessages();

    const raw = this.avisForm.getRawValue();
    this.orderService.deposerAvis(commandeId, {
      qualite: Number(raw.qualite),
      service: Number(raw.service),
      prix: Number(raw.prix),
      description: raw.description.trim()
    }).subscribe({
      next: () => {
        this.actionEnCours.set(false);
        this.fermerPanneauxCommande();
        this.messageGlobal.set('Merci ! Votre avis a été enregistré et sera publié après validation par notre équipe.');
      },
      error: (err) => {
        this.actionEnCours.set(false);
        this.erreurGlobale.set(err?.error?.detail || 'Impossible d’enregistrer votre avis.');
      }
    });
  }

  fermerPanneauxCommande(): void {
    this.commandeEnEditionId.set(null);
    this.commandeEnAnnulationId.set(null);
    this.commandeEnAvisId.set(null);
  }

  // --- Actions sur le profil utilisateur ---

  sauvegarderProfil(): void {
    if (this.profilForm.invalid) {
      this.profilForm.markAllAsTouched();
      return;
    }

    this.actionEnCours.set(true);
    this.resetMessages();

    this.authService.updateProfile(this.profilForm.getRawValue()).subscribe({
      next: () => {
        this.actionEnCours.set(false);
        this.messageGlobal.set('Vos coordonnées personnelles ont bien été mises à jour.');
      },
      error: (err) => {
        this.actionEnCours.set(false);
        this.erreurGlobale.set(err?.error?.detail || 'Erreur lors de la mise à jour du profil.');
      }
    });
  }

  changerMotDePasse(): void {
    if (this.passwordForm.invalid) {
      this.passwordForm.markAllAsTouched();
      return;
    }

    this.actionEnCours.set(true);
    this.resetMessages();

    this.authService.changePassword(this.passwordForm.getRawValue()).subscribe({
      next: (res) => {
        this.actionEnCours.set(false);
        this.passwordForm.reset();
        this.messageGlobal.set(res.message || 'Votre mot de passe a été modifié avec succès.');
      },
      error: (err) => {
        this.actionEnCours.set(false);
        this.erreurGlobale.set(err?.error?.detail || 'Mot de passe actuel incorrect.');
      }
    });
  }

  private resetMessages(): void {
    this.messageGlobal.set(null);
    this.erreurGlobale.set(null);
  }
}