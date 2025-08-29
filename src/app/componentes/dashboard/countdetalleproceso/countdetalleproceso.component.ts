import { Component } from '@angular/core';
import { CountCotizacionesService, CountDetalleProcesos } from '../../servicios/dashboard/CountCotizaciones/count-cotizaciones.service';
import { CommonModule, NgFor } from '@angular/common';
import { FieldsetModule } from 'primeng/fieldset';

@Component({
  selector: 'app-countdetalleproceso',
  imports: [NgFor, CommonModule, FieldsetModule],
  templateUrl: './countdetalleproceso.component.html',
  styleUrl: './countdetalleproceso.component.css'
})
export class CountdetalleprocesoComponent {
constructor(private _srvCountCotizaciones: CountCotizacionesService) { }
  countCotizaciones: CountDetalleProcesos[] = [];

  ngOnInit() {
    this._srvCountCotizaciones.refresh$.subscribe(() => {
       console.log('REFRESH de dashboard activado');
      this.getCountCotizaciones();
    });
    // Llama una vez al inicio
    this.getCountCotizaciones();
  }
  getCountCotizaciones() {
    this._srvCountCotizaciones.getCountDetalleProcesos().subscribe({
      next: (data: any) => {
        this.countCotizaciones = data;
        console.log('Count detalle procesos fetched successfully:', this.countCotizaciones);
      },
      error: (error) => {
        console.error('Error fetching count cotizaciones:', error);
      }
    });
  }
  getEstadoColor(estado: string): string {
    switch (estado) {
      case 'PAGADA': return 'text-green-600';
      case 'POR COBRAR': return 'text-blue-600';
      case 'EN PROCESO': return 'text-yellow-600';
      default: return 'text-gray-600';
    }
  }

}
