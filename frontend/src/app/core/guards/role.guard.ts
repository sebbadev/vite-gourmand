import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { map } from 'rxjs';

import { AuthService } from '../services/auth.service';
import { UserRole } from '../models';

export const roleGuard = (allowedRoles: UserRole[]): CanActivateFn => {
  return (_route, state) => {
    const authService = inject(AuthService);
    const router = inject(Router);

    if (!authService.getToken()) {
      return router.createUrlTree(['/connexion'], {
        queryParams: { returnUrl: state.url }
      });
    }

    const currentUser = authService.currentUserValue;
    if (currentUser) {
      return allowedRoles.includes(currentUser.role)
        ? true
        : router.createUrlTree(['/']);
    }

    return authService.fetchCurrentUser().pipe(
      map((user) => {
        if (!user) {
          return router.createUrlTree(['/connexion'], {
            queryParams: { returnUrl: state.url }
          });
        }
        return allowedRoles.includes(user.role)
          ? true
          : router.createUrlTree(['/']);
      })
    );
  };
};