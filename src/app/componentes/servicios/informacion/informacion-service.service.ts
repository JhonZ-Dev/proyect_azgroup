import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { api_informacion, api_login } from '../../../env/environment';
import { Observable } from 'rxjs';
import { InformacionListResponse, InformacionRead } from '../../modelos/informacion/informacion';

@Injectable({
  providedIn: 'root'
})
export class InformacionServiceService {
  private urlInformacion: string = api_informacion.apiUrl;
  private urlExtract : string = api_login.apiUrl;
  constructor(private http: HttpClient) { }
  private buildHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token');
    return new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: token ? `Bearer ${token}` : ''
    });
  }
  public createInformacion(payload: any) {
    // 1) Lee el token
    const token = localStorage.getItem('access_token');
    //console.log('[InformacionService] token leído de localStorage:', token);
    // 2) Construye las cabeceras
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    });
    // console.log('[InformacionService] cabeceras a enviar:', {
    //   'Content-Type': headers.get('Content-Type'),
    //   Authorization: headers.get('Authorization')
    // });
    // 3) Lanza la petición
    return this.http.post<any>(
      `${this.urlInformacion}create-informacion`,
      payload,
      { headers }
    );
  }

  public getInformacionById(proformaId: number): Observable<InformacionRead> {
    const headers = this.buildHeaders();
    // console.log('[InformacionService] GET  informaciones/', proformaId, ', headers:', headers.get('Authorization'));
    return this.http.get<InformacionRead>(
      `${this.urlInformacion}${proformaId}`,
      { headers }
    );
  }
  public getAllInformaciones(): Observable<InformacionListResponse> {
    // 1) Lee el token
    const token = localStorage.getItem('access_token');
    //console.log('[InformacionService] token leído de localStorage:', token);

    // 2) Construye las cabeceras
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    });
    // console.log('[InformacionService] cabeceras a enviar (GET todas):', {
    //   'Content-Type': headers.get('Content-Type'),
    //   Authorization: headers.get('Authorization')
    // });

    // 3) Lanza la petición
    return this.http.get<InformacionListResponse>(
      `${this.urlInformacion}listar-informaciones`,
      { headers }
    );
  }
  public updateEstado(
    proformaId: number,
    estadoId: number
  ): Observable<InformacionRead> {
    const headers = this.buildHeaders();
    // console.log(
    //   '[InformacionService] PATCH',
    //   `${this.urlInformacion}${proformaId}/estado`,
    //   '-> payload:',
    //   { estado_id: estadoId },
    //   'headers:',
    //   { Authorization: headers.get('Authorization') }
    // );
    return this.http.patch<InformacionRead>(
      `${this.urlInformacion}${proformaId}/estado`,
      { estado_id: estadoId },
      { headers }
    );
  }

public extraerDesdeEnlace(url: string): Observable<any> {
  const headers = this.buildHeaders();
  return this.http.post<any>(
    `${this.urlInformacion}extract`,   // ⬅️ ajusta el endpoint si es diferente
    { url },
    { headers }
  );
}

public fullCreate(payload: any) {
  const headers = this.buildHeaders();
  // Ajusta la ruta según tu router backend
  return this.http.post<any>(
    `${this.urlInformacion}full-create`,
    payload,
    { headers }
  );
}



}
