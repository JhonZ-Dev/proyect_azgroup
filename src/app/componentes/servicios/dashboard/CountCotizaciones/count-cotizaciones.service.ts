import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { api_informacion } from '../../../../env/environment';
import { BehaviorSubject, Observable } from 'rxjs';

export interface CountCotizacionesResponse {
  estado: string;
  total: number;
}

@Injectable({
  providedIn: 'root'
})
export class CountCotizacionesService {

  constructor(private http: HttpClient) { }
  private apiCountCotizaciones: string = api_informacion.apiUrl;
  /** Este subject notificará cuando se deba refrescar el conteo */
  private _refresh$ = new BehaviorSubject<void>(undefined);
// Expón el observable (solo para suscribirse)
  get refresh$(): Observable<void> {
    return this._refresh$.asObservable();
  }

  // Método para disparar el refresh desde cualquier parte
  notifyRefresh() {
    this._refresh$.next();
  }
  private buildHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token');
    return new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: token ? `Bearer ${token}` : ''
    });
  }

  public getCountCotizaciones(): Observable<CountCotizacionesResponse[]> {
    const headers = this.buildHeaders();
    return this.http.get<CountCotizacionesResponse[]>(`${this.apiCountCotizaciones}estadisticas-por-estado`, { headers });
  }

}
