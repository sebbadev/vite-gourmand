import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import { AuthService } from '../../core/services/auth.service';

const PASSWORD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{10,}$/;

@Component({
  selector: 'app-reset-password',
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './reset-password.html',
  styleUrl: './auth-forms.scss'
})
export class ResetPassword implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly authService = inject(AuthService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  resetToken = signal<string | null>(null);
  chargement = signal(false);
  succesMessage = signal<string | null>(null);
  erreurMessage = signal<string | null>(null);

  forgotForm = this.fb.nonNullable.group({
    email: ['', [Validators.required, Validators.email]]
  });

  resetForm = this.fb.nonNullable.group({
    nouveau_password: ['', [Validators.required, Validators.pattern(PASSWORD_REGEX)]]
  });

  ngOnInit(): void {
    const token = this.route.snapshot.queryParamMap.get('token');
    if (token) {
      this.resetToken.set(token);
    }
  }

  onForgotSubmit(): void {
    if (this.forgotForm.invalid) {
      this.forgotForm.markAllAsTouched();
      return;
    }

    this.chargement.set(true);
    this.succesMessage.set(null);
    this.erreurMessage.set(null);

    this.authService.forgotPassword(this.forgotForm.getRawValue()).subscribe({
      next: (res) => {
        this.chargement.set(false);
        this.succesMessage.set(
          res.message || 'Si cette adresse est associée à un compte, un lien de réinitialisation a été envoyé.'
        );
        this.forgotForm.reset();
      },
      error: () => {
        this.chargement.set(false);
        this.erreurMessage.set('Une erreur technique est survenue.');
      }
    });
  }

  onResetSubmit(): void {
    const token = this.resetToken();
    if (!token || this.resetForm.invalid) {
      this.resetForm.markAllAsTouched();
      return;
    }

    this.chargement.set(true);
    this.succesMessage.set(null);
    this.erreurMessage.set(null);

    this.authService.resetPassword({
      token,
      nouveau_password: this.resetForm.controls.nouveau_password.value
    }).subscribe({
      next: () => {
        this.chargement.set(false);
        this.succesMessage.set('Mot de passe mis à jour avec succès. Redirection vers la connexion...');
        setTimeout(() => this.router.navigate(['/connexion']), 2000);
      },
      error: (err) => {
        this.chargement.set(false);
        this.erreurMessage.set(err?.error?.detail || 'Lien invalide ou expiré.');
      }
    });
  }
}