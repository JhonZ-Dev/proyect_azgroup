import { Injectable } from '@angular/core';
import { api_detalleprocesos, api_informacion } from '../../../env/environment';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { ListProcesos, ReporteInformacion } from '../../modelos/procesos/procesos';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ProcesosService {
  private apiUrlDetalleProcesos: string = api_detalleprocesos.apiUrlDetalleProcesos;
  private urlInformacion:string = api_informacion.apiUrl;

  constructor(private http: HttpClient) { }

  private buildHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token');
    return new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: token ? `Bearer ${token}` : ''
    });
  }

  public getAllProcesos(): Observable<ListProcesos[]> {
    const headers = this.buildHeaders();
    return this.http.get<ListProcesos[]>(`${this.apiUrlDetalleProcesos}listar-detallesprocesos`, { headers });
  }

  public updateFirmaEntrega(
  detalleId: number,
  payload: Partial<{ txt_firmacontrato: string; txt_fechaentrega: string }>
): Observable<ListProcesos> {
  const headers = this.buildHeaders();
  return this.http.put<ListProcesos>(
    `${this.apiUrlDetalleProcesos}${detalleId}/firma-entrega`,
    payload,
    { headers }
  );
}


}
