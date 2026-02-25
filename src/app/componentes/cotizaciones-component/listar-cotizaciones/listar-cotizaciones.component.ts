import { Component, QueryList, ViewChild, ViewChildren } from '@angular/core';
import { ItemsServiceService } from '../../servicios/items/items-service.service';
import { InformacionServiceService } from '../../servicios/informacion/informacion-service.service';
import { InformacionRead } from '../../modelos/informacion/informacion';
import { Table, TableModule } from 'primeng/table';
import { ExcelExportService } from '../../servicios/excel-report/excel-export.service';
import { MessageService } from 'primeng/api';
import { ToastModule } from 'primeng/toast';
import { TableRowCollapseEvent, TableRowExpandEvent } from 'primeng/table';
import { CommonModule } from '@angular/common';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { PdfService } from '../../servicios/pdf-service/pdf.service';
import { PdfComponent } from '../../pdf/pdf.component';
import { PaginatorModule } from 'primeng/paginator';
import { Tag, TagModule } from 'primeng/tag';
import { Popover, PopoverModule } from 'primeng/popover';
import { SelectModule } from 'primeng/select';
import { FormsModule } from '@angular/forms';
import { finalize, map } from 'rxjs';
import { FiltrosComponent, OpcionEstados } from '../../filtros/filtros.component';
import { WordService } from '../../servicios/word-service/word.service';
import { HttpResponse } from '@angular/common/http';
import { TooltipModule } from 'primeng/tooltip';
import { CotizacionesComponentComponent } from "../cotizaciones-component.component";
import { CountCotizacionesService } from '../../servicios/dashboard/CountCotizaciones/count-cotizaciones.service';
@Component({
  selector: 'app-listar-cotizaciones',
  imports: [TableModule, ToastModule, CommonModule, ButtonModule, InputTextModule, PaginatorModule, TagModule,
    PopoverModule, SelectModule, FormsModule, FiltrosComponent, TooltipModule],
  templateUrl: './listar-cotizaciones.component.html',
  styleUrl: './listar-cotizaciones.component.css',
  providers: [MessageService],
  standalone: true
})
export class ListarCotizacionesComponent {
  @ViewChild('dt') table!: Table;
  @ViewChildren('itemTable') itemTables!: QueryList<Table>;
  @ViewChild('pdfComp') pdfComp!: PdfComponent;
  @ViewChild('op') op!: Popover;

  constructor(private itemSvc: ItemsServiceService, private infoSvc: InformacionServiceService,
    private excelSvc: ExcelExportService, private pdfSvc: PdfService, private wordSvc: WordService,
    private countCotizacionesService: CountCotizacionesService

  ) { }
  //
  statusOptions = [
    { id: 1, name: 'CREADA' },
    { id: 2, name: 'ENVIADA' },
    { id: 3, name: 'ACEPTADA' },
    { id: 5, name: 'PENDIENTE' },
    { id: 4, name: 'RECHAZADA' }
  ];
  // Paginacion tabla principal
  rows = 10;
  first = 0;
  totalRecords = 0;
  allCotizacionesFiltradas: InformacionRead[] = [];
  // Paginacion items (detalle expandido)
  rows2 = 4;        // cuÃ¡ntas filas mostrar
  first2 = 0;       // Ã­ndice de la primera fila
  cotizaciones: InformacionRead[] = [];
  cotizacion: InformacionRead | null = null;
  error = '';
  loading = false;
  errorMessage = '';
  searchTerm: string = '';
  selectedRow!: InformacionRead;  // aquÃ­ guardaremos â€œcâ€
  selectedStatusOptions!: number;  // <-- aquÃ­ guardaremos solo el id

  ngOnInit() {
    this.loadCotizaciones();
  }

  private loadCotizaciones(): void {
    this.loading = true;

    this.infoSvc.getAllInformaciones().pipe(
      // 1) Ordenar por fecha + hora desc
      map(data => {
        return [...data].sort((a, b) => {
          const ta = new Date(`${a.dFechaRegistro} ${a.tTimeHora}`).getTime();
          const tb = new Date(`${b.dFechaRegistro} ${b.tTimeHora}`).getTime();
          return tb - ta; // las mÃ¡s recientes primero
        });
      }),
      // 2) Desactivar el spinner tanto en Ã©xito como en error
      finalize(() => this.loading = false)
    ).subscribe({
      next: sorted => {
        this.allCotizaciones = sorted;
        this.allCotizacionesFiltradas = [...sorted];
        this.totalRecords = sorted.length;
        this.first = 0;
        this.applyPage();
        console.log('Cotizaciones ordenadas (desc):', this.cotizaciones);
      },
      error: err => {
        console.error('Error cargando cotizaciones', err);
        this.errorMessage = 'No se pudieron cargar las cotizaciones';
      }
    });
  }

  /** Calcula el slice visible de la pÃ¡gina actual */
  private applyPage(): void {
    this.cotizaciones = this.allCotizacionesFiltradas.slice(
      this.first,
      this.first + this.rows
    );
  }

  /** Evento del p-paginator de la tabla principal */
  onPageChange(event: { first?: number; rows?: number }) {
    this.first = event.first ?? 0;
    this.rows = event.rows ?? this.rows;
    this.applyPage();
  }
  public getCotizacionById(proformaId: number): void {
    this.infoSvc.getInformacionById(proformaId).subscribe({
      next: (data: InformacionRead) => {
        console.log('RecibÃ­ esta cotizaciÃ³n:', data);
        this.cotizacion = data;
      },
      error: err => {
        console.error('Error cargando cotizaciÃ³n:', err);
        this.error = 'No se pudo cargar la cotizaciÃ³n';
      }
    });
  }
  abrirEnlace(url: string | undefined | null): void {
    if (!url || typeof url !== 'string' || url.trim() === '') {
      alert('âš ï¸ El enlace no estÃ¡ disponible.');
      return;
    }

    // Si no empieza con http(s), prepÃ©ndelo
    if (!/^https?:\/\//.test(url)) {
      url = 'https://' + url;
    }

    window.open(url, '_blank');
  }





  toggleRow(c: InformacionRead) {
    this.table.toggleRow(c);
  }
  onGlobalFilter(value: string) {
    this.searchTerm = value.trim().toLowerCase();

    // 1) Aplica filtro global a la tabla principal
    this.table.filterGlobal(this.searchTerm, 'contains');
    // 2) Aplica filtro global a cada tabla de detalle (opcional)
    this.itemTables?.forEach(tbl => tbl.filterGlobal(this.searchTerm, 'contains'));

    // 3) Expande automÃ¡ticamente todas las filas filtradas
    //    Si no hay filteredValue (p.ej. aÃºn no filtraste), usa el array completo
    const rowsToExpand: InformacionRead[] =
      (this.table.filteredValue as InformacionRead[]) || this.cotizaciones;

    rowsToExpand.forEach(row => {
      // si no estÃ¡ ya expandida, la abre
      if (!this.table.isRowExpanded(row)) {
        this.table.toggleRow(row);
      }
    });

    // 4) (Opcional) Si borras el buscador, cierras todas las filas
    if (!this.searchTerm) {
      this.cotizaciones.forEach(row => {
        if (this.table.isRowExpanded(row)) {
          this.table.toggleRow(row);
        }
      });
    }
  }
  isMatch(cell: any): boolean {
    if (!this.searchTerm || cell == null) {
      return false;
    }
    return cell.toString().toLowerCase().includes(this.searchTerm);
  }
  cotizacionSeleccionada: InformacionRead | null = null;



  public exportPdfById(proformaId: number): void {
    this.infoSvc.getInformacionById(proformaId).subscribe({
      next: (data: InformacionRead) => {
        //this.pdfSvc.downloadPdfCotizacion(data);
      },
      error: err => {
        console.error('No se pudo cargar la cotizaciÃ³n para PDF', err);
      }
    });
  }
  onPageChange2(event: { first?: number; rows?: number }) {
    this.first2 = event.first ?? 0;
    this.rows2 = event.rows ?? this.rows2;
  }
  expandedNecesidad: { [key: number]: boolean } = {};

  formatText13(txt_especificaciones: string): string {
    return txt_especificaciones.replace(/(.{20})/g, "$1<br>");
  }



  getOverrideStyle(status: string) {
    if (status === 'ENVIADA') {
      return { 'background-color': '#06b6d4', 'color': '#fff', 'border-color': '#06b6d4' };
    }
    if (status === 'ACEPTADA') {
      return { 'background-color': 'rgba(2, 98, 7, 1)', 'color': '#fff', 'border-color': '#14c05eff' };
    }
    if (status === 'CREADA') {
      return { 'background-color': 'rgba(113, 9, 92, 1)', 'color': '#fff', 'border-color': '#c32d82ff' };
    }
    if (status === 'PENDIENTE') {
      return { 'background-color': 'rgba(189, 76, 16, 1)', 'color': '#fff', 'border-color': '#f59048ff' };
    }
    if (status === 'RECHAZADA') {
      return { 'background-color': 'rgba(160, 11, 11, 1)', 'color': '#fff', 'border-color': '#f90909ff' };
    }

    return null; // no toca los demÃ¡s
  }



  toggle(event: any) {
    this.op.toggle(event);
  }



  openPopover(event: Event, row: InformacionRead) {
    this.selectedRow = row;
    this.selectedStatusOptions = row.estado_id;   // carga el valor actual
    this.op.toggle(event);
  }
  onStatusChange() {
    const opt = this.statusOptions.find(o => o.id === this.selectedStatusOptions);
    if (!opt) return;

    // console.log(
    //   `PATCH /informaciones/${this.selectedRow.proforma_id}/estado â†’ payload:`,
    //   { estado_id: this.selectedStatusOptions }
    // );

    this.infoSvc
      .updateEstado(this.selectedRow.proforma_id, this.selectedStatusOptions)
      .subscribe({
        next: () => {
          // actualiza solo el nombre en la UI
          this.selectedRow.estado_id = this.selectedStatusOptions;
          this.selectedRow.estado_name = opt.name;
          // ðŸ‘‡ Notifica a todos los que escuchan que deben refrescar el conteo
          this.countCotizacionesService.notifyRefresh();
        },
        error: err => console.error('No se pudo actualizar estado', err)
      });
  }

  /** MÃ©todo que llama el filtro */
  allCotizaciones: InformacionRead[] = [];
  /** Ahora recibe un nÃºmero (estado_id) */
  onEstadoFilter(estadoId: number | null) {
    if (estadoId != null) {
      this.allCotizacionesFiltradas = this.allCotizaciones.filter(
        c => c.estado_id === estadoId
      );
    } else {
      this.allCotizacionesFiltradas = [...this.allCotizaciones];
    }
    this.totalRecords = this.allCotizacionesFiltradas.length;
    this.first = 0;   // reset paginaciÃ³n tabla principal
    this.first2 = 0;  // reset paginaciÃ³n Ã­tems
    this.applyPage();
  }
  descargarProforma(proformaId: number): void {
    this.wordSvc.descargarProforma(proformaId).subscribe({
      next: (response) => {
        const blob = response.body as Blob;

        if (!blob) {
          console.error('No se recibiÃ³ ningÃºn archivo Word');
          return;
        }

        // ðŸ§  Extraer el nombre desde el header Content-Disposition
        const contentDisposition = response.headers.get('content-disposition');
        let filename = `proforma_${proformaId}.docx`; // Fallback por si no viene

        if (contentDisposition) {
          const match = contentDisposition.match(/filename="?([^"]+)"?/);
          if (match && match[1]) {
            filename = match[1];
          }
        }

        // ðŸ§  Crear la descarga
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();

        // ðŸ§¹ Limpieza
        setTimeout(() => {
          window.URL.revokeObjectURL(url);
        }, 1000);
      },
      error: (err) => {
        console.error('âŒ Error al descargar el archivo Word:', err);
        alert('No se pudo descargar el archivo Word. Intenta nuevamente.');
      }
    });
  }


  // exportToPdf(proformaId:number){
  //   this.pdfSvc.exportToPdf(proformaId).subscribe(blob => {
  //     // Creamos un link temporal y simulamos el click
  //     const url = window.URL.createObjectURL(blob);
  //     const a = document.createElement('a');
  //     a.href = url;
  //     a.download = `proforma_${proformaId}.pdf`;
  //     a.click();
  //     setTimeout(() => window.URL.revokeObjectURL(url), 1000);
  //   });
  // }
  exportToPdf(proformaId: number) {
    this.pdfSvc.exportToPdfs(proformaId).subscribe({
      next: (resp: HttpResponse<Blob>) => {
        const blob = resp.body!;
        let filename = `proforma_${proformaId}.pdf`;
        const contentDisposition = resp.headers.get('content-disposition');
        if (contentDisposition) {
          const match = contentDisposition.match(/filename="?([^"]+)"?/);
          if (match) {
            filename = match[1];
          }
        }
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        setTimeout(() => window.URL.revokeObjectURL(url), 1000);
      },
      error: err => {
        alert('No se pudo descargar el PDF. Intenta nuevamente.');
      }
    });
  }
  exportToExcel(proformaId: number) {
    this.excelSvc.exportToExcel(proformaId).subscribe({
      next: (resp: HttpResponse<Blob>) => {
        const blob = resp.body!;
        let filename = `proforma_${proformaId}.xlsx`;
        const contentDisposition = resp.headers.get('content-disposition');
        if (contentDisposition) {
          const match = contentDisposition.match(/filename="?([^"]+)"?/);
          if (match) {
            filename = match[1];
          }
        }
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        setTimeout(() => window.URL.revokeObjectURL(url), 1000);
      },
      error: err => {
        alert('No se pudo descargar el PDF. Intenta nuevamente.');
      }
    });
  }

  onPagoCreado(resp: any) {
    this.loadCotizaciones();
  }

  esImagen(valor: string | null | undefined): boolean {
    if (!valor) return false;
    const url = valor.trim().toLowerCase();
    // Verifica si parece una URL de imagen
    return /^https?:\/\/.+\.(jpg|jpeg|png|gif|bmp|webp|svg)$/.test(url);
  }
  imagenError(event: Event) {
    const img = event.target as HTMLImageElement;
    img.src = 'https://via.placeholder.com/100x100?text=Sin+imagen'; // ðŸ‘ˆ imagen por defecto
  }
  getProxyImage(url: string): string {
    return 'https://images.weserv.nl/?url=' + encodeURIComponent(url);
  }
  parseEvidencia(valor: string | null | undefined): { imagen?: string, texto?: string } {
    if (!valor) return {};

    const urlRegex = /(https?:\/\/[^\s]+?\.(?:jpg|jpeg|png|gif|bmp|webp|svg|avif))/i;
    const match = valor.match(urlRegex);

    if (match) {
      const imagen = match[0]; //  firt match is the image URL
      const texto = valor.replace(match[0], '').trim(); // todo lo demÃ¡s como texto
      return { imagen, texto };
    } else {
      return { texto: valor.trim() };
    }
  }



}
