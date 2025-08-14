// auth.guard.ts
import { Injectable } from '@angular/core';
import {
  CanActivate, Router
} from '@angular/router';
import { LoginServiceService } from '../servicios/login/login-service.service';
@Injectable({ providedIn: 'root' })
export class AuthGuard implements CanActivate {
  constructor(
    private auth: LoginServiceService,
    private router: Router
  ) {}
  canActivate(): boolean {
    if (this.auth.isLoggedIn()) return true;
    this.router.navigate(['/login']);
    return false;
  }
}
