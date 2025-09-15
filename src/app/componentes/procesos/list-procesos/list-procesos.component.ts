import { Component } from '@angular/core';
import { ProcesosService } from '../../servicios/procesos/procesos.service';
import { ListProcesos, ReporteInformacion } from '../../modelos/procesos/procesos';
import { finalize, map } from 'rxjs';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-list-procesos',
  imports: [CommonModule],
  templateUrl: './list-procesos.component.html',
  styleUrl: './list-procesos.component.css',
  standalone: true,
})
export class ListProcesosComponent {

  constructor(private _srvProcesos: ProcesosService) { }
  procesos: ListProcesos[] = []
  allProcesos: ListProcesos[] = [];
  infoProcesos: ReporteInformacion[] = []
  error = '';
  loading = false;
  errorMessage = '';

  ngOnInit() {
    this.loadProcesos();
    this.loadInfoProcesos();
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


  private loadInfoProcesos(): void {
    this._srvProcesos.getAllInfProcesos().subscribe({
      next: (data: ReporteInformacion[]) => {
        this.infoProcesos = data;
        console.log('Información de procesos cargada:', this.infoProcesos);
      },
      error: (err) => {
        console.error('Error cargando información de procesos', err);
        this.errorMessage = 'No se pudo cargar la información de los procesos';
      }
    });
  }

}
