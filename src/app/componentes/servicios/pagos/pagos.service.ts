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
    return this.http.post<PagosCreate>(`${this.apiPagos}crear-pago`, payload, { headers });
  }

}
