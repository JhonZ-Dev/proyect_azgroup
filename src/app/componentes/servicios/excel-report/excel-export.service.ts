import { Injectable } from '@angular/core';
import { Workbook } from 'exceljs';
import { saveAs } from 'file-saver';
import { api_informacion } from '../../../env/environment';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root',
})
export class ExcelExportService {
  constructor(private http: HttpClient) { }
  private apiExcelUrl: string = api_informacion.apiUrl;

  exportToExcel(proformaId: number) {
    return this.http.get(`${this.apiExcelUrl}descargar-excel/${proformaId}`, {
      responseType: 'blob',
      observe: 'response'
    });
  }
}
