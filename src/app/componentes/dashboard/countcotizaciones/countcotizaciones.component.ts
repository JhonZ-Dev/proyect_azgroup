import { Component, OnInit } from '@angular/core';
import { CountCotizacionesResponse, CountCotizacionesService } from '../../servicios/dashboard/CountCotizaciones/count-cotizaciones.service';
import { CommonModule, NgFor } from '@angular/common';
import { FieldsetModule } from 'primeng/fieldset';

@Component({
  selector: 'app-countcotizaciones',
  imports: [NgFor, CommonModule, FieldsetModule],
  templateUrl: './countcotizaciones.component.html',
  styleUrl: './countcotizaciones.component.css',
  standalone: true
})
export class CountcotizacionesComponent implements OnInit {


  constructor(private _srvCountCotizaciones: CountCotizacionesService) { }
  countCotizaciones: CountCotizacionesResponse[] = [];

  ngOnInit() {
    this._srvCountCotizaciones.refresh$.subscribe(() => {
       //console.log('REFRESH de dashboard activado');
      this.getCountCotizaciones();
    });
    // Llama una vez al inicio
    this.getCountCotizaciones();
  }
  getCountCotizaciones() {
    this._srvCountCotizaciones.getCountCotizaciones().subscribe({
      next: (data: any) => {
        this.countCotizaciones = data;
        //console.log('Count Cotizaciones fetched successfully:', this.countCotizaciones);
      },
      error: (error) => {
        console.error('Error fetching count cotizaciones:', error);
      }
    });
  }
  getEstadoColor(estado: string): string {
    switch (estado) {
      case 'ACEPTADA': return 'text-emerald-500';
      case 'CREADA': return 'text-blue-500';
      case 'ENVIADA': return 'text-indigo-500';
      case 'PENDIENTE': return 'text-amber-500';
      case 'RECHAZADA': return 'text-red-500';
      default: return 'text-slate-500';
    }
  }

  getCardBorder(estado: string): string {
    switch (estado) {
      case 'ACEPTADA': return 'card-border-green';
      case 'CREADA': return 'card-border-blue';
      case 'ENVIADA': return 'card-border-indigo';
      case 'PENDIENTE': return 'card-border-orange';
      case 'RECHAZADA': return 'card-border-red';
      default: return 'card-border-default';
    }
  }

  getIconClass(estado: string): string {
    switch (estado) {
      case 'ACEPTADA': return 'pi-check-circle';
      case 'CREADA': return 'pi-file-edit';
      case 'ENVIADA': return 'pi-send';
      case 'PENDIENTE': return 'pi-clock';
      case 'RECHAZADA': return 'pi-times-circle';
      default: return 'pi-box';
    }
  }

}
