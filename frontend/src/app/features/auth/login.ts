import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-login',
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './login.html',
  styleUrl: './auth-forms.scss'
})
export class Login {
  private readonly fb = inject(FormBuilder);
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);

  chargement = signal(false);
  erreurMessage = signal<string | null>(null);

  loginForm = this.fb.nonNullable.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required]]
  });

  onSubmit(): void {
    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      return;
    }

    this.chargement.set(true);
    this.erreurMessage.set(null);

    this.authService.login(this.loginForm.getRawValue()).subscribe({
      next: (user) => {
        this.chargement.set(false);
        if (!user) {
          this.erreurMessage.set('Impossible de récupérer votre profil utilisateur.');
          return;
        }

        // Redirection intelligente selon returnUrl ou selon le rôle métier
        const returnUrl = this.route.snapshot.queryParamMap.get('returnUrl');
        if (returnUrl) {
          this.router.navigateByUrl(returnUrl);
        } else if (user.role === 'Administrateur') {
          this.router.navigate(['/admin']);
        } else if (user.role === 'Employé') {
          this.router.navigate(['/employe']);
        } else {
          this.router.navigate(['/catalogue']);
        }
      },
      error: (err) => {
        this.chargement.set(false);
        this.erreurMessage.set(err?.error?.detail || 'Identifiants invalides.');
      }
    });
  }
}