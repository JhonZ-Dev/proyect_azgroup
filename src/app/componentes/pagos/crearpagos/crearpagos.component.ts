import { Component, EventEmitter, Input, Output } from '@angular/core';
import { PagosService } from '../../servicios/pagos/pagos.service';
import { PagosCreate } from '../../modelos/pagos/pagos';
import { ButtonModule } from 'primeng/button';
import { Dialog, DialogModule } from 'primeng/dialog';
import { FieldsetModule } from 'primeng/fieldset';
import { InputTextModule } from 'primeng/inputtext';
import { SelectModule } from 'primeng/select';
import { CommonModule } from '@angular/common';
import { FormControl, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { DatePickerModule } from 'primeng/datepicker';



export interface FormasPago {
  id: number;
  name: string;
}
@Component({
  selector: 'app-crearpagos',
  imports: [ButtonModule, DialogModule, FieldsetModule, InputTextModule, SelectModule, CommonModule, FormsModule, ReactiveFormsModule,
    DatePickerModule
  ],
  templateUrl: './crearpagos.component.html',
  styleUrl: './crearpagos.component.css',
  standalone: true
})

export class CrearpagosComponent {

  constructor(private srvPagos: PagosService) { }
  formaspagos: FormasPago[] | undefined;
  selectedformasPagos: FormasPago | undefined;
  @Input() visible = false;
  @Output() visibleChange = new EventEmitter<boolean>();
  @Output() pagoCreado = new EventEmitter<any>();
  pagos: PagosCreate = {
    txtFormaPago: '',
    txtUsuarioPaga: '',
    txtUsuarioRecibe: '',
    dFechaPago: '',
    tHoraPago: '',
    txtUsuarioCorreo: '',
    txtMontoPagar: 0,
    txtMongoPagarTexto: '',
    estado_id: 0
  };

  ngOnInit() {
    this.formaspagos = [
      { id: 1, name: 'Efectivo' },
      { id: 2, name: 'Transferencia' }
    ];
  }

  //formulario reactivos
  pagosForm = new FormGroup({
    txtUsuarioPaga: new FormControl('', Validators.required),
    txtUsuarioRecibe: new FormControl('', Validators.required),
    txtUsuarioCorreo: new FormControl('', [Validators.required, Validators.email]),
    //formaPago: new FormControl(null, Validators.required),
    formaPago: new FormControl<FormasPago | null>(null, Validators.required), // <-- aquí!
    txtMontoPagar: new FormControl(0, [Validators.required, Validators.min(0)]),

  });
  showDialog() {
    this.visible = true;
  }

  crearPago() {
    if (this.pagosForm.valid) {
      const datos = this.pagosForm.value;
      const ahora = new Date();
      const dFechaPago = ahora.toISOString().slice(0, 10);
      const tHoraPago = ahora.toTimeString().slice(0, 8);
      const monto = datos.txtMontoPagar ?? 0;
      const txtMongoPagarTexto = this.numeroATexto(monto) + ' dólares';
      const pago: PagosCreate = {
        txtFormaPago: datos.formaPago?.name ?? '',
        txtUsuarioPaga: datos.txtUsuarioPaga ?? '',
        txtUsuarioRecibe: datos.txtUsuarioRecibe ?? '',
        dFechaPago,
        tHoraPago,
        txtUsuarioCorreo: datos.txtUsuarioCorreo ?? '',
        txtMontoPagar: datos.txtMontoPagar ?? 0,
        txtMongoPagarTexto,
        estado_id: 2
      };
      console.log('Pago a crear:', pago);
      // this.srvPagos.createPago(pago).subscribe({
      //   next: (resp) => {
      //     alert('Pago creado correctamente');
      //     this.pagosForm.reset();
      //   },
      //   error: (err) => {
      //     alert('Error al crear el pago');
      //   }
      // });

    } else {
      this.pagosForm.markAllAsTouched();
      alert('Faltan campos obligatorios');
    }
  }

  limpiarFormulario() {
    this.pagos = {
      txtFormaPago: '',
      txtUsuarioPaga: '',
      txtUsuarioRecibe: '',
      dFechaPago: '',
      tHoraPago: '',
      txtUsuarioCorreo: '',
      txtMontoPagar: 0,
      txtMongoPagarTexto: '',
      estado_id: 0
    };
  }

numeroATexto(n: number): string {
  // Solo básicos hasta 999, puedes extender más si necesitas
  const unidades = ['','uno','dos','tres','cuatro','cinco','seis','siete','ocho','nueve'];
  const decenas = ['','diez','veinte','treinta','cuarenta','cincuenta','sesenta','setenta','ochenta','noventa'];
  const centenas = ['','cien','doscientos','trescientos','cuatrocientos','quinientos','seiscientos','setecientos','ochocientos','novecientos'];

  if (n === 0) return 'cero';
  if (n < 10) return unidades[n];
  if (n < 100) {
    if (n % 10 === 0) return decenas[Math.floor(n / 10)];
    return decenas[Math.floor(n / 10)] + ' y ' + unidades[n % 10];
  }
  if (n < 1000) {
    if (n % 100 === 0) return centenas[Math.floor(n / 100)];
    return centenas[Math.floor(n / 100)] + ' ' + this.numeroATexto(n % 100);
  }
  return n.toString(); // Si quieres más, implementa miles/millones
}
onHide() {
  this.visible = false;
  this.visibleChange.emit(false); // <-- actualiza al padre
}

onShow() {
  this.visible = true;
  this.visibleChange.emit(true); // opcional, por simetría
}

// Si cierras programáticamente después de crear:
private cerrarDialog() {
  this.visible = false;
  this.visibleChange.emit(false);
}


}
