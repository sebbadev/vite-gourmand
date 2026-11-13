import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { switchMap } from 'rxjs';

import { AuthService } from '../../core/services/auth.service';

// Politique ANSSI/RGPD : min 10 caractères, 1 majuscule, 1 minuscule, 1 chiffre, 1 caractère spécial
const PASSWORD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{10,}$/;

@Component({
  selector: 'app-register',
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './register.html',
  styleUrl: './auth-forms.scss'
})
export class Register {
  private readonly fb = inject(FormBuilder);
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  chargement = signal(false);
  erreurMessage = signal<string | null>(null);

  registerForm = this.fb.nonNullable.group({
    prenom: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(50)]],
    nom: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(50)]],
    email: ['', [Validators.required, Validators.email]],
    telephone: ['', [Validators.required, Validators.maxLength(20)]],
    adresse: ['', [Validators.maxLength(255)]],
    code_postal: ['', [Validators.maxLength(10)]],
    ville: ['', [Validators.maxLength(50)]],
    password: ['', [Validators.required, Validators.pattern(PASSWORD_REGEX)]]
  });

  onSubmit(): void {
    if (this.registerForm.invalid) {
      this.registerForm.markAllAsTouched();
      return;
    }

    this.chargement.set(true);
    this.erreurMessage.set(null);

    const raw = this.registerForm.getRawValue();
    const payload = {
      ...raw,
      adresse: raw.adresse.trim() || undefined,
      code_postal: raw.code_postal.trim() || undefined,
      ville: raw.ville.trim() || undefined
    };

    this.authService.register(payload).pipe(
      switchMap(() => this.authService.login({ email: raw.email, password: raw.password }))
    ).subscribe({
      next: () => {
        this.chargement.set(false);
        this.router.navigate(['/catalogue']);
      },
      error: (err) => {
        this.chargement.set(false);
        this.erreurMessage.set(err?.error?.detail || 'Erreur lors de la création du compte.');
      }
    });
  }
}
