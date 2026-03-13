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
       //console.log('REFRESH de dashboard activado');
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
      case 'PAGADA': return 'text-emerald-500';
      case 'POR COBRAR': return 'text-indigo-500';
      case 'EN PROCESO': return 'text-amber-500';
      default: return 'text-slate-500';
    }
  }

  getCardBorder(estado: string): string {
    switch (estado) {
      case 'PAGADA': return 'card-border-green';
      case 'POR COBRAR': return 'card-border-indigo';
      case 'EN PROCESO': return 'card-border-orange';
      default: return 'card-border-default';
    }
  }

  getIconClass(estado: string): string {
    switch (estado) {
      case 'PAGADA': return 'pi-dollar';
      case 'POR COBRAR': return 'pi-wallet';
      case 'EN PROCESO': return 'pi-sync';
      default: return 'pi-file';
    }
  }

}
