import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../componentes/servicios/auth/auth.service';

export const loggedInGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);
  if (auth.isAuthenticated()) {
    // Ya está logueado; mándalo al menú
    router.navigate(['/menu-principal'], { replaceUrl: true });
    return false;
  }
  return true;
};
