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
@Component({
  selector: 'app-listar-cotizaciones',
  imports: [TableModule, ToastModule, CommonModule, ButtonModule, InputTextModule, PaginatorModule, TagModule,
    PopoverModule, SelectModule, FormsModule, FiltrosComponent, TooltipModule
  ],
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
    private excelSvc: ExcelExportService, private pdfSvc: PdfService, private wordSvc: WordService

  ) { }
  //
  statusOptions = [
    { id: 1, name: 'CREADA' },
    { id: 2, name: 'ENVIADA' },
    { id: 3, name: 'ACEPTADA' },
    { id: 5, name: 'PENDIENTE' },
    { id: 4, name: 'RECHAZADA' }
  ];
  rows2 = 4;        // cuántas filas mostrar
  first2 = 0;       // índice de la primera fila
  cotizaciones: InformacionRead[] = [];
  cotizacion: InformacionRead | null = null;
  error = '';
  loading = false;
  errorMessage = '';
  searchTerm: string = '';
  selectedRow!: InformacionRead;  // aquí guardaremos “c”
  selectedStatusOptions!: number;  // <-- aquí guardaremos solo el id

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
          return tb - ta; // las más recientes primero
        });
      }),
      // 2) Desactivar el spinner tanto en éxito como en error
      finalize(() => this.loading = false)
    ).subscribe({
      next: sorted => {
        this.allCotizaciones = sorted;
        this.cotizaciones = [...sorted];;
        console.log('Cotizaciones ordenadas (desc):', this.cotizaciones);
      },
      error: err => {
        console.error('Error cargando cotizaciones', err);
        this.errorMessage = 'No se pudieron cargar las cotizaciones';
      }
    });
  }
  public getCotizacionById(proformaId: number): void {
    this.infoSvc.getInformacionById(proformaId).subscribe({
      next: (data: InformacionRead) => {
        console.log('Recibí esta cotización:', data);
        this.cotizacion = data;
      },
      error: err => {
        console.error('Error cargando cotización:', err);
        this.error = 'No se pudo cargar la cotización';
      }
    });
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

    // 3) Expande automáticamente todas las filas filtradas
    //    Si no hay filteredValue (p.ej. aún no filtraste), usa el array completo
    const rowsToExpand: InformacionRead[] =
      (this.table.filteredValue as InformacionRead[]) || this.cotizaciones;

    rowsToExpand.forEach(row => {
      // si no está ya expandida, la abre
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
        console.error('No se pudo cargar la cotización para PDF', err);
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


  getSeverity(status: string): 'success' | 'secondary' | 'info' | 'warn' | 'danger' | 'contrast' {
    switch (status) {
      case 'ACEPTADA':
        return 'success';
      case 'CREADA':
        return 'info';
      case 'ENVIADA':
        return 'info';
      case 'PENDIENTE':
        return 'warn';       // ← cambió de warning a warn
      case 'RECHAZADA':
        return 'danger';
      default:
        return 'secondary';  // o 'info', lo que prefieras para estados desconocidos
    }
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

    console.log(
      `PATCH /informaciones/${this.selectedRow.proforma_id}/estado → payload:`,
      { estado_id: this.selectedStatusOptions }
    );

    this.infoSvc
      .updateEstado(this.selectedRow.proforma_id, this.selectedStatusOptions)
      .subscribe({
        next: () => {
          // actualiza solo el nombre en la UI
          this.selectedRow.estado_name = opt.name;
        },
        error: err => console.error('No se pudo actualizar estado', err)
      });
  }

  /** Método que llama el filtro */
  allCotizaciones: InformacionRead[] = [];
  /** Ahora recibe un número (estado_id) */
  onEstadoFilter(estadoId: number | null) {
    if (estadoId != null) {
      this.cotizaciones = this.allCotizaciones.filter(
        c => c.estado_id === estadoId
      );
    } else {
      this.cotizaciones = [...this.allCotizaciones];
    }
    this.first2 = 0; // reset paginación si usas paginador manual
  }
  descargarProforma(proformaId: number) {
    this.wordSvc.descargarProforma(proformaId)
      .subscribe(blob => {
        // Creamos un link temporal y simulamos el click
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `proforma_${proformaId}.docx`;
        a.click();
        setTimeout(() => window.URL.revokeObjectURL(url), 1000);
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



}
