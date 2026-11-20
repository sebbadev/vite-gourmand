import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { map } from 'rxjs';

import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = (_route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  // Cas 1 : Aucun jeton stocké -> redirection immédiate vers la connexion
  if (!authService.getToken()) {
    return router.createUrlTree(['/connexion'], {
      queryParams: { returnUrl: state.url }
    });
  }

  // Cas 2 : L'utilisateur est déjà hydraté en mémoire
  if (authService.currentUserValue) {
    return true;
  }

  // Cas 3 : Jeton présent (ex: après un F5), on attend la réponse de /auth/me
  return authService.fetchCurrentUser().pipe(
    map((user) => {
      if (user) {
        return true;
      }
      return router.createUrlTree(['/connexion'], {
        queryParams: { returnUrl: state.url }
      });
    })
  );
};