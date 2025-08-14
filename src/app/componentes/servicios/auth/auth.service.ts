import { inject, Injectable } from '@angular/core';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private router = inject(Router);
  private TOKEN_KEY = 'access_token';
  constructor() { }
  get token(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  isAuthenticated(): boolean {
    const t = this.token;
    return !!t && t.trim().length > 0;
  }

  setToken(token: string) {
    localStorage.setItem(this.TOKEN_KEY, token);
  }

  logout() {
    // Limpia TODO lo relacionado con sesión
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem('menus');

    // Navega a login y reemplaza la entrada del historial
    this.router.navigate(['/login'], { replaceUrl: true });
  }
}
