import { Injectable } from '@angular/core';
import { api_login } from '../../../env/environment';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { catchError, tap, throwError } from 'rxjs';
import { JwtHelperService } from '@auth0/angular-jwt';
export interface DecodedToken {
  sub: string;
  roles: string[];
  exp: number;
}
@Injectable({
  providedIn: 'root'
})
export class LoginServiceService {
  private urlLogin:string = api_login.apiUrl;
  private jwtHelper = new JwtHelperService();

  constructor(private http:HttpClient) { }

  //iniciar sesion
  // 1) Login: guardamos token en localStorage
public login(username: string, password: string) {
    // Construimos el body form-url-encoded
    const body = new HttpParams()
      .set('grant_type', 'password')
      .set('username', username)
      .set('password', password);

    // Y especificamos el content-type
    const headers = new HttpHeaders({
      'Content-Type': 'application/x-www-form-urlencoded'
    });

    return this.http
      .post<any>(this.urlLogin+"token", body.toString(), {
        headers,
        withCredentials: true  // si usas cookies HttpOnly
      })
      .pipe(
        catchError((error) => throwError(error))
      );
  }

  // 2) Obtener token
  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  // 3) Saber si está logueado (existe token y no expiró)
  isLoggedIn(): boolean {
    const token = this.getToken();
    if (!token) return false;
    // Comprueba expiración si quieres
    return !this.jwtHelper.isTokenExpired(token);
  }

  // 4) Logout
  logout(): void {
    localStorage.removeItem('access_token');
  }
   // Nuevo: decodificar token
  getDecodedToken(): DecodedToken | null {
    const token = this.getToken();
    if (!token) return null;
    try {
      return this.jwtHelper.decodeToken(token) as DecodedToken;
    } catch {
      return null;
    }
  }
    // Nuevo: obtener sólo el nombre de usuario (campo sub)
  getUsername(): string | null {
    const decoded = this.getDecodedToken();
    return decoded?.sub ?? null;
  }
}
