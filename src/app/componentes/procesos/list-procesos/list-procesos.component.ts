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
import { SelectModule } from 'primeng/select';
@Component({
  selector: 'app-list-procesos',
  imports: [CommonModule, TableModule, ToastModule, FormsModule, InputTextModule, SelectModule],
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
  estados: { label: string; value: number }[] = []; // para p-dropdown
  totalPagado: number = 0;
  totalPorCobrar: number = 0;
  totalEnProceso: number = 0;

  ngOnInit() {
    this.loadProcesos();
    this.loadEstados();
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
        this.procesos = [...sorted];
        this.calcularTotal();
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

  private loadEstados() {
    this._srvProcesos.getEstadosDetalle().subscribe({
      next: (rows) => {
        this.estados = rows.map(r => ({ label: r.estado, value: r.estado_id }));
      },
      error: (err) => console.error('Error cargando estados', err)
    });
  }
  enableEditEstado(detalleId: number) {
    this.editingField[detalleId] = 'estado';
  }
  onEstadoChange(proceso: ListProcesos, newEstadoId: number) {
    this._srvProcesos.updateEstadoDetalle(proceso.detalle_id, newEstadoId).subscribe({
      next: (res) => {
        proceso.estado_name = res.estado_name; // backend devuelve estado_name actualizado
        proceso.estado_id = res.estado_id as any; // si lo tienes en el modelo, útil para binding
        this.calcularTotal();
        this.message.add({ severity: 'success', summary: 'Estado actualizado', detail: `Nuevo estado: ${proceso.estado_name}`, life: 2000 });
        
        this.editingField[proceso.detalle_id] = null;
      },
      error: (err) => {
        console.error('Error actualizando estado', err);
        this.message.add({ severity: 'error', summary: 'Error', detail: 'No se pudo actualizar el estado', life: 3000 });
        this.editingField[proceso.detalle_id] = null;
      }
    });
  }
  getEstadoClass(p: ListProcesos): string {
    const name = (p?.estado_name || '').toUpperCase().trim();
    if (name === 'PAGADO') return 'row-pagado';
    if (name === 'POR COBRAR') return 'row-por-cobrar';
    if (name === 'EN PROCESO') return 'row-en-proceso';
    return '';
  }

  totalContratos: number = 0;

private calcularTotal(): void {
  const toCents = (v: any): number => {
    const n = typeof v === 'string'
      ? Number(v.replace(/[^\d.-]/g, '').replace(/,/g, ''))
      : Number(v);
    return Math.round((n || 0) * 100);
  };

  let totalCents = 0;
  let pagado = 0;
  let porCobrar = 0;
  let enProceso = 0;

  this.procesos.forEach(p => {
    const cents = toCents(p.int_valor_contrato);
    totalCents += cents;

    const estado = (p.estado_name || '').toUpperCase().trim();
    if (estado === 'PAGADO') pagado += cents;
    else if (estado === 'POR COBRAR') porCobrar += cents;
    else if (estado === 'EN PROCESO') enProceso += cents;
  });

  this.totalContratos = totalCents / 100;
  this.totalPagado = pagado / 100;
  this.totalPorCobrar = porCobrar / 100;
  this.totalEnProceso = enProceso / 100;
}



}
