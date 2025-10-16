import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { api_pagos } from '../../../env/environment';
import { PagosCreate, PagosRead } from '../../modelos/pagos/pagos';

@Injectable({
  providedIn: 'root'
})
export class PagosService {

  constructor(private http:HttpClient) { }
  private apiPagos:string= api_pagos.apiUrlPagos;
  private buildHeaders(): HttpHeaders {
      const token = localStorage.getItem('access_token');
      return new HttpHeaders({
        'Content-Type': 'application/json',
        Authorization: token ? `Bearer ${token}` : ''
      });
    }
  //listar pagos
  public getPagosById(proformaId: number) {
    const headers = this.buildHeaders();
    return this.http.get(`${this.apiPagos}listar-pagos/${proformaId}`, { headers });
  }
  //listar todos los pagos
  public getAllPagos() {
    const headers = this.buildHeaders();
    return this.http.get<PagosRead[]>(`${this.apiPagos}listar-pagos`, { headers });
  }

  //crear pago
  public createPago(payload: PagosCreate) {
    const headers = this.buildHeaders();
    return this.http.post<PagosCreate>(`${this.apiPagos}crear-pago/email`, payload, { headers });
  }

  public createPagoFormData(formData: FormData) {
  const token = localStorage.getItem('access_token');
  const headers = new HttpHeaders({
    Authorization: token ? `Bearer ${token}` : ''
    // No pongas Content-Type → Angular lo infiere automáticamente como multipart/form-data
  });
  return this.http.post(`${this.apiPagos}crear-pago/email`, formData, { headers });
}


}
