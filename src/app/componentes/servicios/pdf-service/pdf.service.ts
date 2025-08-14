// src/app/services/pdf.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { InformacionRead, ItemRead } from '../../modelos/informacion/informacion';
import { api_informacion } from '../../../env/environment';

@Injectable({ providedIn: 'root' })
export class PdfService {

  constructor(private http: HttpClient) { }
  private apiPdfUrl: string = api_informacion.apiUrl;

  exportToPdf(proformaId: number) {
    // Indicamos que la respuesta es un blob (archivo)
    return this.http.get(
      `${this.apiPdfUrl}descargar-pdf/${proformaId}`,
      { responseType: 'blob' }
    );
  }

  exportToPdfs(proformaId: number) {
  return this.http.get(`${this.apiPdfUrl}descargar-pdf/${proformaId}`, {
    responseType: 'blob',
    observe: 'response'
  });
}





}
