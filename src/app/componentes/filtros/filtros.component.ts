import { Component, EventEmitter, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { PopoverModule } from 'primeng/popover';
import { SelectModule } from 'primeng/select';


export interface OpcionEstados{
  id:number;
  name:string;
}
@Component({
  selector: 'app-filtros',
  imports: [PopoverModule, SelectModule,FormsModule],
  templateUrl: './filtros.component.html',
  styleUrl: './filtros.component.css'
})
export class FiltrosComponent {
   statusOptions = [
    { id: 1, name: 'CREADA' },
    { id: 2, name: 'ENVIADA' },
    { id: 3, name: 'ACEPTADA' },
    { id: 5, name: 'PENDIENTE' },
    { id: 4, name: 'RECHAZADA' }
  ];
  selectedOptionEstados: OpcionEstados | undefined;
// Evento que emitirá el estado elegido
/** Ahora emitimos un number, no un objeto */
  @Output() estadoChange = new EventEmitter<number>();

  onSelectChange(id: number) {
    this.estadoChange.emit(id);
  }

}
