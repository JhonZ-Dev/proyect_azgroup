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
      case 'ACEPTADA': return 'text-green-600';
      case 'CREADA': return 'text-blue-600';
      case 'ENVIADA': return 'text-yellow-600';
      case 'PENDIENTE': return 'text-orange-600';
      case 'RECHAZADA': return 'text-red-600';
      default: return 'text-gray-600';
    }
  }

}
