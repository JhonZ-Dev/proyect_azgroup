import { Injectable } from '@angular/core';
import { api_exportToWord } from '../../../env/environment';
import { HttpClient, HttpHeaders } from '@angular/common/http';
@Injectable({
  providedIn: 'root'
})
export class WordService {

  constructor(private http: HttpClient) { }
  private apiWord: string = api_exportToWord.apiUrl
  private buildHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token');
    return new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: token ? `Bearer ${token}` : ''
    });
  }


  descargarProforma(proformaId: number) {
    // Indicamos que la respuesta es un blob (archivo)
    return this.http.get(
      `${this.apiWord}descargar-proforma/${proformaId}`,
      { responseType: 'blob' }
    );
  }
}
