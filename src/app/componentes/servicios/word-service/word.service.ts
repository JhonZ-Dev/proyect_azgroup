import { Injectable } from '@angular/core';
import { api_exportToWord } from '../../../env/environment';
import { HttpClient, HttpHeaders, HttpResponse } from '@angular/common/http';
import { Observable } from 'rxjs';
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


descargarProforma(proformaId: number): Observable<HttpResponse<Blob>> {
    return this.http.get(`${this.apiWord}descargar-proforma/${proformaId}`, {
      responseType: 'blob',
      observe: 'response'
    });
  }
}
