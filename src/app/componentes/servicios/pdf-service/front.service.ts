// src/app/services/pdf.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import jsPDF from 'jspdf';
import { InformacionRead, ItemRead } from '../../modelos/informacion/informacion';

@Injectable({ providedIn: 'root' })
export class PdfService {
  private bgBase64: string | null = null;
  
  constructor(private http: HttpClient) { }

  private loadBackground(): Promise<void> {
    if (this.bgBase64) return Promise.resolve();
    return new Promise((resolve, reject) => {
      this.http
        .get('assets/fondomembretada.jpg', { responseType: 'blob' })
        .subscribe(blob => {
          const reader = new FileReader();
          reader.onload = () => {
            this.bgBase64 = reader.result as string;
            resolve();
          };
          reader.onerror = err => reject(err);
          reader.readAsDataURL(blob);
        }, err => reject(err));
    });
  }

  /**
   * Obtiene o asigna un número secuencial de 6 dígitos para la proforma basada en el NIC.
   * Siempre será único y persistente en el navegador para cada txt_necesidad (NIC).
   */
  private getProformaNumber(nic: string): string {
    const storageKey = 'proforma_numbers';
    let mapa: Record<string, number> = {};

    // Lee el mapa de localStorage (si existe)
    try {
      const raw = localStorage.getItem(storageKey);
      if (raw) mapa = JSON.parse(raw);
    } catch (err) {
      // Si hay error, empieza con vacío
      mapa = {};
    }

    // Si el NIC ya tiene un número, devuelve el mismo
    if (nic in mapa) {
      return mapa[nic].toString().padStart(6, '0');
    }

    // Asigna el siguiente número
    const maxUsed = Object.values(mapa).length > 0 ? Math.max(...Object.values(mapa)) : 0;
    const nextNumber = maxUsed + 1;

    // Guarda en el mapa y en localStorage
    mapa[nic] = nextNumber;
    localStorage.setItem(storageKey, JSON.stringify(mapa));
    return nextNumber.toString().padStart(6, '0');
  }

  // Función auxiliar para controlar saltos de página
  private ensureSpace(
    doc: jsPDF,
    y: number,
    neededHeight: number,
    marginTop: number,
    pageHeight: number,
    marginBottom: number
  ): number {
    const maxY = pageHeight - marginBottom;
    if (y + neededHeight > maxY) {
      doc.addPage();
      // Redibuja el fondo si tienes imagen
      if (this.bgBase64) {
        doc.addImage(this.bgBase64, 'JPEG', 0, 0, 612, 792);
      }
      return marginTop;
    }
    return y;
  }

  // ---- MÉTODO PRINCIPAL DINÁMICO ----
  async downloadPdfCotizacion(cotizacion: InformacionRead) {
    await this.loadBackground();

    const doc = new jsPDF({
      unit: 'pt',
      format: 'letter',
      orientation: 'portrait',
    });

    // Dimensiones y márgenes
    const pageWidth = 612, pageHeight = 792;
    const marginLeft = 43, marginRight = 43, marginTop = 85, marginBottom = 71;
    const usableWidth = pageWidth - marginLeft - marginRight;

    // Fondo
    if (this.bgBase64) {
      doc.addImage(this.bgBase64, 'JPEG', 0, 0, pageWidth, pageHeight);
    }

    let y = marginTop;
    const rowHeight = 16;
    const col1Width = 110;
    const col2Width = usableWidth - col1Width;
    const proformaNic = cotizacion.txt_necesidad || 'SIN-NIC';
    const proformaNumber = this.getProformaNumber(proformaNic);

    // ---- PROFORMA ----
    y = this.ensureSpace(doc, y, rowHeight, marginTop, pageHeight, marginBottom);
    doc.setDrawColor(0, 0, 0);
    doc.setFillColor(218, 233, 247);
    doc.rect(marginLeft, y, usableWidth, rowHeight, 'FD');
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(10);
    doc.setTextColor(0, 0, 0);
    doc.text(`PROFORMA  ${proformaNumber}`, marginLeft + usableWidth / 2, y + rowHeight / 2 + 4, { align: 'center', baseline: 'middle' });
    doc.setFillColor(255, 255, 255);
    y += rowHeight;

    // ---- Datos de cabecera (dinámico) ----
    const fields = [
      { label: 'CLIENTE', key: 'txt_cliente' },
      { label: 'RUC', key: 'txt_ruc' },
      { label: 'DIRECCIÓN:', key: 'txt_direccion' },
      { label: 'FECHA', key: 'txt_fecha' },
      { label: 'TELEFONO', key: 'txt_telefono' },
      { label: 'NECESIDAD', key: 'txt_necesidad' },
      { label: 'FUNCIONARIO ENCARGADO:', key: 'txt_funcionario' },
      { label: 'CORREO', key: 'txt_correo' },
      { label: '  :', key: 'tHora_maxina' },
    ];

    for (let i = 0; i < fields.length; i++) {
      const value = (cotizacion as any)[fields[i].key] ?? '';
      const fieldLines = doc.splitTextToSize(fields[i].label, col1Width - 12);
      const valueLines = doc.splitTextToSize(value, col2Width - 12);
      const numLines = Math.max(fieldLines.length, valueLines.length);
      const dynamicRowHeight = 18 * numLines;

      // Salto de página si es necesario
      y = this.ensureSpace(doc, y, dynamicRowHeight, marginTop, pageHeight, marginBottom);

      // --- Etiqueta ---
      doc.setDrawColor(0, 0, 0);
      doc.setFillColor(232, 242, 254);
      doc.rect(marginLeft, y, col1Width, dynamicRowHeight, 'FD');
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(10);
      doc.setTextColor(0, 0, 0);
      doc.text(fieldLines, marginLeft + 6, y + 14);

      // --- Valor ---
      if (fields[i].label === 'CORREO') {
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(11);
        doc.setTextColor(0, 0, 0);
        doc.text(valueLines, marginLeft + col1Width + 6, y + 14);
        // Subrayado solo la primera línea
        const firstLineWidth = doc.getTextWidth(valueLines[0]);
        doc.setDrawColor(0, 0, 200);
        doc.setLineWidth(0.7);
        doc.line(
          marginLeft + col1Width + 6,
          y + 18,
          marginLeft + col1Width + 6 + firstLineWidth,
          y + 18
        );
        doc.setDrawColor(0, 0, 0);
        doc.setTextColor(0, 0, 0);
      } else if (fields[i].label === 'NECESIDAD') {
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(10);
        doc.setTextColor(220, 38, 38);
        doc.text(valueLines, marginLeft + col1Width + 6, y + 14);
        doc.setTextColor(0, 0, 0);
      } else {
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(10);
        doc.setTextColor(0, 0, 0);
        doc.text(valueLines, marginLeft + col1Width + 6, y + 14);
      }
      doc.rect(marginLeft + col1Width, y, col2Width, dynamicRowHeight);
      y += dynamicRowHeight;
    }

    // ---- OBJETO DE COMPRA (dinámico) ----
    y = this.ensureSpace(doc, y, rowHeight, marginTop, pageHeight, marginBottom);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(10);
    doc.rect(marginLeft, y, usableWidth, rowHeight);
    doc.text('OBJETO DE COMPRA', marginLeft + 6, y + rowHeight / 2 + 3, { baseline: 'middle' });
    y += rowHeight;

    // Descripción del objeto
    const desc = cotizacion.txt_objetivoCompra ?? '';
    const descLines = doc.splitTextToSize(desc, usableWidth - 12);
    const descRowHeight = 16 * descLines.length;
    y = this.ensureSpace(doc, y, descRowHeight, marginTop, pageHeight, marginBottom);
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(10);
    doc.rect(marginLeft, y, usableWidth, descRowHeight);
    doc.text(descLines, marginLeft + 6, y + 14);
    y += descRowHeight;

    // ---- TABLA DE ITEMS DINÁMICA ----
    const colHeaders = ['No.', 'CPC', 'UNIDAD', 'ESPECIFICACIONES', 'CANTIDAD', 'P. UNIT', 'P.TOTAL'];
    const colWidths = [30, 60, 55, 190, 45, 73, 73]; // suma = 526

    let colX = marginLeft;

    // Encabezados
    y = this.ensureSpace(doc, y, rowHeight, marginTop, pageHeight, marginBottom);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(9);
    colX = marginLeft;
    for (let i = 0; i < colHeaders.length; i++) {
      doc.rect(colX, y, colWidths[i], rowHeight);
      doc.text(colHeaders[i], colX + 4, y + rowHeight / 2 + 3, { baseline: 'middle' });
      colX += colWidths[i];
    }
    y += rowHeight;

    // Filas dinámicas de items con altura adaptativa
    let total = 0;
    if (Array.isArray(cotizacion.items)) {
      cotizacion.items.forEach((item: ItemRead, idx: number) => {
        colX = marginLeft;
        const itemRow = [
          (idx + 1).toString(),
          item.txt_cpc,
          item.txt_unidad,
          item.txt_especificaciones ?? '',
          String(item.int_cantidad),
          item.flo_precioUnitario != null ? ('$' + item.flo_precioUnitario.toLocaleString('en-US', { minimumFractionDigits: 2 })) : '',
          item.flo_precioTotal != null ? ('$' + item.flo_precioTotal.toLocaleString('en-US', { minimumFractionDigits: 2 })) : ''
        ];
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(9);

        // 1. Calcula la cantidad máxima de líneas para la fila
        const linesPerCell = itemRow.map((txt, i) =>
          doc.splitTextToSize(txt, colWidths[i] - 8).length
        );
        const maxLines = Math.max(...linesPerCell);
        const dynamicRowHeight = 14 * maxLines; // 14 pt por línea para mejor ajuste

        // Salto de página si es necesario para la fila de items
        y = this.ensureSpace(doc, y, dynamicRowHeight, marginTop, pageHeight, marginBottom);

        // 2. Dibuja cada celda, ajustando el alto
        colX = marginLeft;
        for (let j = 0; j < itemRow.length; j++) {
          const lines = doc.splitTextToSize(itemRow[j], colWidths[j] - 8);
          doc.rect(colX, y, colWidths[j], dynamicRowHeight);
          doc.text(lines, colX + 4, y + 12); // 12 pt para mejor verticalidad en celdas multi-línea
          colX += colWidths[j];
        }
        // Suma total (solo si hay valor)
        if (typeof item.flo_precioTotal === 'number') total += item.flo_precioTotal;
        y += dynamicRowHeight;
      });
    }

    // ---- FILA DE TOTAL ----
    const totalLabelWidth = colWidths.slice(0, colWidths.length - 1).reduce((a, b) => a + b, 0);
    const totalValueWidth = colWidths[colWidths.length - 1];
    colX = marginLeft;

    y = this.ensureSpace(doc, y, rowHeight, marginTop, pageHeight, marginBottom);

    doc.setFont('helvetica', 'bold');
    doc.setFontSize(10);
    doc.setDrawColor(0, 0, 0);
    doc.setFillColor(255, 239, 203); // Amarillo claro

    // Celdas combinadas para "TOTAL"
    doc.rect(colX, y, totalLabelWidth, rowHeight, 'FD');
    doc.text('TOTAL', colX + totalLabelWidth / 2, y + rowHeight / 2 + 4, {
      align: 'center', baseline: 'middle'
    });
    colX += totalLabelWidth;

    // Celda de suma final
    const totalFormatted = '$' + total.toLocaleString('en-US', { minimumFractionDigits: 2 });
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(11);
    doc.setTextColor(25, 120, 25); // Verde oscuro
    doc.rect(colX, y, totalValueWidth, rowHeight, 'FD');
    doc.text(totalFormatted, colX + totalValueWidth / 2, y + rowHeight / 2 + 4, {
      align: 'center', baseline: 'middle'
    });
    doc.setTextColor(0, 0, 0); // Regresa a negro
    //NUEVA FILA
    y += rowHeight;

    y = this.ensureSpace(doc, y, rowHeight, marginTop, pageHeight, marginBottom);

    doc.setDrawColor(0, 0, 0);
    doc.setFillColor(255, 226, 226); // Fondo rosa claro
    doc.rect(marginLeft, y, usableWidth, rowHeight, 'FD');
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(11);
    doc.setTextColor(220, 38, 38); // Rojo fuerte
    doc.text(
      'NO GRAVAMOS IVA - SOMOS REGIMEN RIMPE - NEGOCIO POPULAR',
      marginLeft + usableWidth / 2,
      y + rowHeight / 2 + 4,
      { align: 'center', baseline: 'middle' }
    );
    doc.setTextColor(0, 0, 0);
    y += rowHeight;

    // ---- Datos de finales (dinámico) ----
    const fields_final = [
      { label: 'PLAZO DE ENTREGA', key: 'txt_plazoEntrega' },
      { label: 'VIGENCIA DE LA OFERTA', key: 'txt_vigenciaOferta' },
      { label: 'FORMA DE PAGO:', key: 'txt_formaPago' },
      { label: 'METODOLOGIA DE TRABAJO', key: 'txt_metodologiaTrabajo' },
      { label: 'GARANTIA', key: 'txt_garantia' },
      { label: 'ENLACE', key: 'txt_enlace' }
    ];
    for (let i = 0; i < fields_final.length; i++) {
      const value = (cotizacion as any)[fields_final[i].key] ?? '';
      const fieldLines = doc.splitTextToSize(fields_final[i].label, col1Width - 12);
      const valueLines = doc.splitTextToSize(value, col2Width - 12);
      const numLines = Math.max(fieldLines.length, valueLines.length);
      const dynamicRowHeight = 18 * numLines;

      y = this.ensureSpace(doc, y, dynamicRowHeight, marginTop, pageHeight, marginBottom);

      // --- Etiqueta ---
      doc.setDrawColor(0, 0, 0);
      doc.setFillColor(232, 242, 254);
      doc.rect(marginLeft, y, col1Width, dynamicRowHeight, 'FD');
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(10);
      doc.setTextColor(0, 0, 0);
      doc.text(fieldLines, marginLeft + 6, y + 14);

      // --- Valor ---
      if (fields_final[i].label === 'CORREO') {
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(11);
        doc.setTextColor(0, 0, 0);
        doc.text(valueLines, marginLeft + col1Width + 6, y + 14);
        // Subrayado solo la primera línea
        const firstLineWidth = doc.getTextWidth(valueLines[0]);
        doc.setDrawColor(0, 0, 200);
        doc.setLineWidth(0.7);
        doc.line(
          marginLeft + col1Width + 6,
          y + 18,
          marginLeft + col1Width + 6 + firstLineWidth,
          y + 18
        );
        doc.setDrawColor(0, 0, 0);
        doc.setTextColor(0, 0, 0);
      } else if (fields_final[i].label === 'NECESIDAD') {
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(10);
        doc.setTextColor(220, 38, 38);
        doc.text(valueLines, marginLeft + col1Width + 6, y + 14);
        doc.setTextColor(0, 0, 0);
      } else {
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(10);
        doc.setTextColor(0, 0, 0);
        doc.text(valueLines, marginLeft + col1Width + 6, y + 14);
      }
      doc.rect(marginLeft + col1Width, y, col2Width, dynamicRowHeight);
      y += dynamicRowHeight;
    }
    const signatureSpace = 54; // ~2 líneas en 28pt o más si quieres
    y += signatureSpace;
    // Verifica si hay espacio suficiente para el bloque de la firma
    const firmaHeight = 60; // Estima el espacio de tu bloque de firma
    y = this.ensureSpace(doc, y, firmaHeight, marginTop, pageHeight, marginBottom);
    // --- Nombre en negrita, azul oscuro y centrado (Times New Roman)
    doc.setFont('times', 'bold');
    doc.setFontSize(11);
    doc.setTextColor(0, 32, 96); // Azul oscuro
    doc.text(
      'DAYANA LISBETH ZAMBRANO MACIAS',
      marginLeft + usableWidth / 2,
      y,
      { align: 'center', baseline: 'top' }
    );

    // --- Cargo y RUC, normal, negro, centrado
    doc.setFont('times', 'normal');
    doc.setFontSize(11);
    doc.setTextColor(0, 0, 0);
    doc.text(
      'REPRESENTE LEGAL',
      marginLeft + usableWidth / 2,
      y + 18,
      { align: 'center', baseline: 'top' }
    );
    doc.text(
      'RUC: 2350621211001',
      marginLeft + usableWidth / 2,
      y + 34,
      { align: 'center', baseline: 'top' }
    );
    // ¡Listo!
    doc.save('documento.pdf');
  }
}
