import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { CurrencyPipe, DatePipe } from '@angular/common';

import { BackofficeService } from '../../core/services/backoffice.service';
import { CatalogueService } from '../../core/services/catalogue.service';
import { VitrineService } from '../../core/services/vitrine.service';

import {
  Avis,
  CatalogueFilters,
  ContactMode,
  ContactRead,
  EquipmentStatus,
  Horaire,
  MenuListItem,
  OrderRead,
  OrderStatus,
  PaymentStatus,
  Plat
} from '../../core/models';

@Component({
  selector: 'app-employe-dashboard',
  imports: [ReactiveFormsModule, CurrencyPipe, DatePipe],
  templateUrl: './employe-dashboard.html',
  styleUrl: './employe-dashboard.scss'
})
export class EmployeDashboard implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly backofficeService = inject(BackofficeService);
  private readonly catalogueService = inject(CatalogueService);
  private readonly vitrineService = inject(VitrineService);

  ongletActif = signal<'commandes' | 'catalogue' | 'avis' | 'horaires'>('commandes');
  messageSucces = signal<string | null>(null);
  messageErreur = signal<string | null>(null);
  actionEnCours = signal(false);

  // Données des 4 onglets
  commandes = signal<OrderRead[]>([]);
  activesUniquement = signal(true);
    // Filtres combinés instantanés (Client + 3 statuts)
  filtreClient = signal<string>('');
  filtreStatutCmd = signal<string>('');
  filtreStatutPay = signal<string>('');
  filtreStatutMat = signal<string>('');

  // Liste unique des clients présents dans les commandes chargées
  clientsDisponibles = computed(() => {
    const map = new Map<number, string>();
    for (const cmd of this.commandes()) {
      if (!map.has(cmd.user_id)) {
        const nomComplet = cmd.client
          ? `${cmd.client.prenom} ${cmd.client.nom} (${cmd.client.email})`
          : `Client #${cmd.user_id}`;
        map.set(cmd.user_id, nomComplet);
      }
    }
    return Array.from(map.entries()).map(([id, label]) => ({ id, label }));
  });

  // Commandes filtrées en temps réel
  commandesFiltrees = computed(() => {
    const clientId = this.filtreClient();
    const stCmd = this.filtreStatutCmd();
    const stPay = this.filtreStatutPay();
    const stMat = this.filtreStatutMat();

    return this.commandes().filter((cmd) => {
      if (clientId && cmd.user_id !== Number(clientId)) return false;
      if (stCmd && cmd.statut !== stCmd) return false;
      if (stPay && cmd.statut_paiement !== stPay) return false;
      if (stMat && cmd.statut_materiel !== stMat) return false;
      return true;
    });
  });

  reinitialiserFiltresCommandes(): void {
    this.filtreClient.set('');
    this.filtreStatutCmd.set('');
    this.filtreStatutPay.set('');
    this.filtreStatutMat.set('');
  }
  menus = signal<MenuListItem[]>([]);
  plats = signal<Plat[]>([]);
  referentiels = signal<CatalogueFilters>({ themes: [], regimes: [], allergenes: [] });
  avisList = signal<Avis[]>([]);
  horaires = signal<Horaire[]>([]);
  contacts = signal<ContactRead[]>([]);

  // Sélections pour création rapide de menu
  selectedPlatIds = signal<number[]>([]);
  selectedThemeIds = signal<number[]>([]);

  // Formulaire de création d'un nouveau menu
  menuForm = this.fb.nonNullable.group({
    titre: ['', [Validators.required, Validators.maxLength(50)]],
    nombre_personnes_min: [6, [Validators.required, Validators.min(1)]],
    prix_par_personne: [28, [Validators.required, Validators.min(1)]],
    quantite_disponible: [50, [Validators.required, Validators.min(0)]],
    images_url: ['/assets/images/menus/prestige.webp', [Validators.required, Validators.maxLength(255)]],
    description: ['', [Validators.required, Validators.minLength(10)]]
  });

  // Panneau d'annulation employé (avec audit de contact obligatoire)
  commandeAnnulationId = signal<number | null>(null);
  cancelEmployeForm = this.fb.nonNullable.group({
    motif_annulation: ['', [Validators.required, Validators.minLength(5)]],
    mode_contact_annulation: ['Téléphone' as ContactMode, [Validators.required]],
    contact_client_effectue: [false, [Validators.requiredTrue]]
  });

  readonly statutsCommande: OrderStatus[] = [
    'En attente de validation',
    'Acceptée',
    'En préparation',
    'En cours de livraison',
    'Livrée',
    'Terminée'
  ];
  readonly statutsPaiement: PaymentStatus[] = ['En attente de règlement', 'Réglée', 'Annulée'];
  readonly statutsMateriel: EquipmentStatus[] = ['Inclus', 'Non inclus', 'Retourné'];

  ngOnInit(): void {
    this.chargerCommandes();
    this.chargerCatalogue();
    this.chargerAvis();
    this.chargerHorairesEtContacts();
  }

  // --- 1. Commandes ---

  chargerCommandes(): void {
    this.backofficeService.getToutesCommandes(this.activesUniquement()).subscribe({
      next: (data) => this.commandes.set(data),
      error: () => this.messageErreur.set('Erreur lors du chargement des commandes.')
    });
  }

  basculerFiltreCommandes(): void {
    this.activesUniquement.update((v) => !v);
    this.chargerCommandes();
  }

  mettreAJourStatuts(
    cmd: OrderRead,
    nouveauStatut: string,
    statutPaiement: string,
    statutMateriel: string
  ): void {
    this.resetMessages();
    this.actionEnCours.set(true);

    this.backofficeService.updateStatutCommande(cmd.commande_id, {
      nouveau_statut: nouveauStatut as OrderStatus,
      statut_paiement: statutPaiement as PaymentStatus,
      statut_materiel: statutMateriel as EquipmentStatus
    }).subscribe({
      next: (updated) => {
        this.actionEnCours.set(false);
        this.messageSucces.set(
          updated.statut === 'Terminée'
            ? `Commande ${updated.numero_commande} clôturée (Terminée) et synchronisée avec MongoDB Stats !`
            : `Statuts de la commande ${updated.numero_commande} mis à jour.`
        );
        this.chargerCommandes();
      },
      error: (err) => {
        this.actionEnCours.set(false);
        this.messageErreur.set(err?.error?.detail || 'Transition de statut refusée par les règles métier.');
      }
    });
  }

  /** Retourne le statut suivant dans le cycle de vie, ou null si déjà terminée/annulée */
  getStatutSuivant(statutActuel: OrderStatus): OrderStatus | null {
    const idx = this.statutsCommande.indexOf(statutActuel);
    if (idx === -1 || idx >= this.statutsCommande.length - 1) {
      return null;
    }
    return this.statutsCommande[idx + 1];
  }

  /** Passe directement la commande à l'étape suivante en conservant paiement et matériel */
  passerStatutSuivant(cmd: OrderRead): void {
    const suivant = this.getStatutSuivant(cmd.statut);
    if (!suivant) return;
    this.mettreAJourStatuts(cmd, suivant, cmd.statut_paiement, cmd.statut_materiel);
  }

  ouvrirAnnulationEmploye(commandeId: number): void {
    this.commandeAnnulationId.set(commandeId);
    this.cancelEmployeForm.reset({
      motif_annulation: '',
      mode_contact_annulation: 'Téléphone',
      contact_client_effectue: false
    });
  }

  confirmerAnnulationEmploye(commandeId: number): void {
    if (this.cancelEmployeForm.invalid) {
      this.cancelEmployeForm.markAllAsTouched();
      return;
    }

    this.resetMessages();
    this.actionEnCours.set(true);

    this.backofficeService.annulerCommandeEmploye(commandeId, this.cancelEmployeForm.getRawValue()).subscribe({
      next: () => {
        this.actionEnCours.set(false);
        this.commandeAnnulationId.set(null);
        this.messageSucces.set('Commande annulée avec audit de contact enregistré et stock restitué.');
        this.chargerCommandes();
      },
      error: (err) => {
        this.actionEnCours.set(false);
        this.messageErreur.set(err?.error?.detail || 'Impossible d’annuler cette commande.');
      }
    });
  }

  // --- 2. Catalogue (Menus & Plats) ---

  chargerCatalogue(): void {
    this.catalogueService.getMenus().subscribe({ next: (data) => this.menus.set(data) });
    this.backofficeService.getPlats().subscribe({ next: (data) => this.plats.set(data) });
    this.catalogueService.getFiltres().subscribe({ next: (data) => this.referentiels.set(data) });
  }

  toggleSelectionId(listSignal: ReturnType<typeof signal<number[]>>, id: number): void {
    listSignal.update((ids) => (ids.includes(id) ? ids.filter((x) => x !== id) : [...ids, id]));
  }

  creerMenu(): void {
    if (this.menuForm.invalid) {
      this.menuForm.markAllAsTouched();
      return;
    }

    this.resetMessages();
    this.actionEnCours.set(true);

    const raw = this.menuForm.getRawValue();
    this.backofficeService.createMenu({
      ...raw,
      is_active: true,
      plat_ids: this.selectedPlatIds(),
      theme_ids: this.selectedThemeIds()
    }).subscribe({
      next: (created) => {
        this.actionEnCours.set(false);
        this.messageSucces.set(`Le menu « ${created.titre} » a été publié dans le catalogue.`);
        this.menuForm.reset({
          titre: '',
          nombre_personnes_min: 6,
          prix_par_personne: 28,
          quantite_disponible: 50,
          images_url: '/assets/images/menus/prestige.webp',
          description: ''
        });
        this.selectedPlatIds.set([]);
        this.selectedThemeIds.set([]);
        this.chargerCatalogue();
      },
      error: (err) => {
        this.actionEnCours.set(false);
        this.messageErreur.set(err?.error?.detail || 'Erreur lors de la création du menu.');
      }
    });
  }

  supprimerMenu(menu: MenuListItem): void {
    this.resetMessages();
    this.backofficeService.deleteMenu(menu.menu_id).subscribe({
      next: () => {
        this.messageSucces.set(`Le menu « ${menu.titre} » a été archivé (suppression logique).`);
        this.chargerCatalogue();
      },
      error: () => this.messageErreur.set('Impossible de supprimer ce menu.')
    });
  }

  // --- 3. Modération des Avis MongoDB ---

  chargerAvis(): void {
    this.backofficeService.getAvisAdmin().subscribe({
      next: (data) => this.avisList.set(data)
    });
  }

  modererAvis(avisId: string, statut: 'Approuvé' | 'Rejeté'): void {
    this.resetMessages();
    this.backofficeService.modererAvis(avisId, { statut }).subscribe({
      next: () => {
        this.messageSucces.set(`Avis marqué comme « ${statut} » dans MongoDB.`);
        this.chargerAvis();
      },
      error: () => this.messageErreur.set('Erreur lors de la modération de l’avis.')
    });
  }

  // --- 4. Horaires & Messages Contact ---

  chargerHorairesEtContacts(): void {
    this.vitrineService.getHoraires().subscribe({ next: (data) => this.horaires.set(data) });
    this.backofficeService.getContactsAdmin().subscribe({ next: (data) => this.contacts.set(data) });
  }

  sauvegarderHoraire(h: Horaire, ouverture: string, fermeture: string): void {
    this.resetMessages();
    const ouv = ouverture.length === 5 ? `${ouverture}:00` : ouverture;
    const ferm = fermeture.length === 5 ? `${fermeture}:00` : fermeture;

    this.backofficeService.updateHoraire(h.horaire_id, {
      heure_ouverture: ouv,
      heure_fermeture: ferm
    }).subscribe({
      next: () => {
        this.messageSucces.set(`Horaires du ${h.jour} mis à jour.`);
        this.chargerHorairesEtContacts();
      },
      error: (err) => this.messageErreur.set(err?.error?.detail || 'Horaire invalide.')
    });
  }

  marquerTraite(contactId: string): void {
    this.resetMessages();
    this.backofficeService.marquerContactTraite(contactId).subscribe({
      next: () => {
        this.messageSucces.set('Message marqué comme traité.');
        this.chargerHorairesEtContacts();
      }
    });
  }

  private resetMessages(): void {
    this.messageSucces.set(null);
    this.messageErreur.set(null);
  }
}