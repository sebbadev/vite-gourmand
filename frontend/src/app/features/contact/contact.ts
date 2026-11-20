import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { VitrineService } from '../../core/services/vitrine.service';
import { ContactCreate } from '../../core/models';

@Component({
  selector: 'app-contact',
  imports: [ReactiveFormsModule],
  templateUrl: './contact.html',
  styleUrl: './contact.scss'
})
export class Contact {
  private readonly fb = inject(FormBuilder);
  private readonly vitrineService = inject(VitrineService);

  envoiEnCours = signal(false);
  succesMessage = signal<string | null>(null);
  erreurMessage = signal<string | null>(null);

  contactForm = this.fb.nonNullable.group({
    nom: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(50)]],
    prenom: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(50)]],
    email: ['', [Validators.required, Validators.email]],
    telephone: ['', [Validators.maxLength(20)]],
    objet: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(120)]],
    message: ['', [Validators.required, Validators.minLength(10), Validators.maxLength(2000)]],
    rgpd_consent: [false, [Validators.requiredTrue]]
  });

  onSubmit(): void {
    if (this.contactForm.invalid) {
      this.contactForm.markAllAsTouched();
      return;
    }

    this.envoiEnCours.set(true);
    this.succesMessage.set(null);
    this.erreurMessage.set(null);

    const raw = this.contactForm.getRawValue();
    const payload: ContactCreate = {
      ...raw,
      telephone: raw.telephone.trim() || undefined
    };

    this.vitrineService.envoyerContact(payload).subscribe({
      next: () => {
        this.envoiEnCours.set(false);
        this.succesMessage.set('Votre message a bien été transmis à notre équipe. Nous vous répondrons sous 24h.');
        this.contactForm.reset();
      },
      error: (err) => {
        this.envoiEnCours.set(false);
        this.erreurMessage.set(err?.error?.detail || 'Une erreur est survenue lors de l’envoi du message.');
      }
    });
  }
}