import { Component, EventEmitter, Output } from '@angular/core';
import { ItemsServiceService } from '../../servicios/items/items-service.service';
import { InformacionServiceService } from '../../servicios/informacion/informacion-service.service';
import { FormBuilder, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MessageService } from 'primeng/api';
import { LoginServiceService } from '../../servicios/login/login-service.service';
import { CommonModule } from '@angular/common';
import { InputTextModule } from 'primeng/inputtext';
import { ButtonModule } from 'primeng/button';
import { InputNumberModule } from 'primeng/inputnumber';
import { TextareaModule } from 'primeng/textarea';
import { InputGroupModule } from 'primeng/inputgroup';
import { InputGroupAddonModule } from 'primeng/inputgroupaddon';
import { Toast } from 'primeng/toast';
import { DialogModule } from 'primeng/dialog';
import { FloatLabel } from 'primeng/floatlabel';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { InformacionRead } from '../../modelos/informacion/informacion';

@Component({
  selector: 'app-update-cotizaciones',
 imports: [FormsModule,CommonModule,InputTextModule, ButtonModule, InputNumberModule, TextareaModule, InputGroupModule, InputGroupAddonModule],
  templateUrl: './update-cotizaciones.component.html',
  styleUrl: './update-cotizaciones.component.css'
})
export class UpdateCotizacionesComponent {
  
  searchCode: string = '';   // 🔹 valor del input
  loading = false;
  cotizacion: InformacionRead | null = null;
  @Output() cotizacionEncontrada = new EventEmitter<InformacionRead>();

  constructor(private itemSvc: ItemsServiceService, private infoSvc: InformacionServiceService, private fb: FormBuilder, private messageService: MessageService, private loginSvc: LoginServiceService) { }

  buscarPorNecesidad() {
    if (!this.searchCode.trim()) {
      this.messageService.add({severity: 'warn', summary: 'Atención', detail: 'Ingrese un código de necesidad'});
      return;
    }

    this.loading = true;

    this.infoSvc.getInformacionByNecesidad(this.searchCode.trim()).subscribe({
      next: (resp) => {
        this.loading = false;
        this.messageService.add({severity: 'success', summary: 'Éxito', detail: 'Información cargada'});
        this.cotizacionEncontrada.emit(resp);  // 👈 envías al padre
      },
      error: (err) => {
        this.loading = false;
        this.messageService.add({severity: 'error', summary: 'Error', detail: 'No se encontró información'});
        console.error('❌ Error buscando necesidad:', err);
      }
    });
  }
}
