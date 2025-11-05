import { Component } from '@angular/core';
import { ProcesosService } from '../../servicios/procesos/procesos.service';
import { ListProcesos, ReporteInformacion } from '../../modelos/procesos/procesos';
import { finalize, map } from 'rxjs';
import { CommonModule } from '@angular/common';
import { TableModule } from 'primeng/table';
import { ToastModule } from 'primeng/toast';
import { FormsModule } from '@angular/forms';
import { MessageService } from 'primeng/api';
import { InputTextModule } from 'primeng/inputtext';
@Component({
  selector: 'app-list-procesos',
  imports: [CommonModule, TableModule, ToastModule, FormsModule, InputTextModule],
  templateUrl: './list-procesos.component.html',
  styleUrl: './list-procesos.component.css',
  standalone: true,
  providers: [MessageService]
})
export class ListProcesosComponent {

  constructor(private _srvProcesos: ProcesosService, private message: MessageService) { }
  procesos: ListProcesos[] = []
  allProcesos: ListProcesos[] = [];
  infoProcesos: ReporteInformacion[] = []
  error = '';
  loading = false;
  errorMessage = '';
  editingField: { [id: number]: string | null } = {}; // {detalle_id: 'campo'}

  ngOnInit() {
    this.loadProcesos();
  }

  private loadProcesos(): void {
    this.loading = true;

    this._srvProcesos.getAllProcesos().pipe(
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
        this.allProcesos = sorted;
        this.procesos = [...sorted];;
        console.log('Procesos ordenadas (desc):', this.procesos);
      },
      error: err => {
        console.error('Error cargando cotizaciones', err);
        this.errorMessage = 'No se pudieron cargar las cotizaciones';
      }
    });
  }

   enableEdit(detalleId: number, field: 'txt_firmacontrato' | 'txt_fechaentrega') {
    this.editingField[detalleId] = field;
  }

onBlurOrEnter(proceso: ListProcesos, field: 'txt_firmacontrato' | 'txt_fechaentrega') {
    const value = proceso[field];
    const payload: any = {};
    payload[field] = value;

    this._srvProcesos.updateFirmaEntrega(proceso.detalle_id, payload).subscribe({
      next: (res) => {
        proceso.txt_firmacontrato = res.txt_firmacontrato;
        proceso.txt_fechaentrega = res.txt_fechaentrega;
        proceso.txt_fechafin = res.txt_fechafin;
        proceso.int_diasmora = res.int_diasmora;

        this.message.add({
          severity: 'success',
          summary: 'Actualizado',
          detail: `Campo ${field === 'txt_firmacontrato' ? 'Firma de contrato' : 'Fecha de entrega'} actualizado`,
          life: 2500,
        });

        this.editingField[proceso.detalle_id] = null;
      },
      error: (err) => {
        console.error('Error actualizando', err);
        this.message.add({
          severity: 'error',
          summary: 'Error',
          detail: 'No se pudo actualizar el proceso',
          life: 3000,
        });
        this.editingField[proceso.detalle_id] = null;
      },
    });
  }



}
