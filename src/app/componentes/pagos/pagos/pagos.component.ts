import { Component } from '@angular/core';
import { PagosService } from '../../servicios/pagos/pagos.service';
import { PagosRead } from '../../modelos/pagos/pagos';
import { Observable } from 'rxjs';
import { CrearpagosComponent } from '../crearpagos/crearpagos.component';
import { ButtonModule } from 'primeng/button';
import { Dialog, DialogModule } from 'primeng/dialog';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { TooltipModule } from 'primeng/tooltip';
@Component({
  selector: 'app-pagos',
  imports: [CrearpagosComponent, ButtonModule, DialogModule, CommonModule, FormsModule, TableModule,
    TagModule, TooltipModule
  ],
  templateUrl: './pagos.component.html',
  styleUrl: './pagos.component.css',
  standalone: true
})
export class PagosComponent {
  constructor(private srvPagos: PagosService) { }
  pagos: PagosRead[] = [];
  pago: PagosRead | null = null;
  modalVisible = false;
  imagenSeleccionada: string | null = null;
  mostrarImagen: boolean = false;
  ngOnInit() {
    this.getAllPagos();
    this.verificarSiPuedeCrearPago();
  }

  getAllPagos() {
    this.srvPagos.getAllPagos().subscribe({
      next: (data: PagosRead[]) => {
        this.pagos = data;
        console.log('Pagos fetched successfully:', this.pagos);
      },
      error: (error) => {
        console.error('Error fetching pagos:', error);
      }
    });
  }
  abrirDialog() {
    this.modalVisible = true;
  }

  onPagoCreado(resp: any) {
    this.getAllPagos();
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
        return 'info';  // o 'info', lo que prefieras para estados desconocidos
    }
  }
  abrirImagen(url: string) {
    this.imagenSeleccionada = url;
    this.mostrarImagen = true;
  }

  cerrarImagen() {
    this.mostrarImagen = false;
    this.imagenSeleccionada = null;
  }


  puedeCrearPago: boolean = false;
  verificarSiPuedeCrearPago() {
    const hoy = new Date();
    const dia = hoy.getDate();

    // Habilita el botón solo si hoy es día 15
    this.puedeCrearPago = (dia === 16);
  }
}
