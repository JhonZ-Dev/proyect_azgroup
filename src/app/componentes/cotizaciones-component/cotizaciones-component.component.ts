import { Component, EventEmitter, Input, Output } from '@angular/core';
import { ItemsServiceService } from '../servicios/items/items-service.service';
import { InformacionServiceService } from '../servicios/informacion/informacion-service.service';
import { FormArray, FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { combineLatest, forkJoin, startWith, switchMap } from 'rxjs';
import { CommonModule } from '@angular/common';
import { InputTextModule } from 'primeng/inputtext';
import { ButtonModule } from 'primeng/button';
import { InputNumberModule } from 'primeng/inputnumber';
import { TextareaModule } from 'primeng/textarea';
import { InputGroupModule } from 'primeng/inputgroup';
import { InputGroupAddonModule } from 'primeng/inputgroupaddon';
import { MessageService } from 'primeng/api';
import { Toast } from 'primeng/toast';
import { DialogModule } from 'primeng/dialog';
@Component({
  selector: 'app-cotizaciones-component',
  imports: [FormsModule, CommonModule, ReactiveFormsModule, InputTextModule, ButtonModule, InputNumberModule, TextareaModule, InputGroupModule, InputGroupAddonModule, Toast, DialogModule],
  templateUrl: './cotizaciones-component.component.html',
  styleUrl: './cotizaciones-component.component.css',
  standalone: true,
  providers: [MessageService]
})
export class CotizacionesComponentComponent {
  
  cotizacionForm!: FormGroup;
  private lastGroupValid = false;
  lastQtyPuSet: any;

  constructor(private itemSvc: ItemsServiceService, private infoSvc: InformacionServiceService, private fb: FormBuilder, private messageService: MessageService) { }

  ngOnInit() {
    this.cotizacionForm = this.fb.group({
      txt_cliente: ['', Validators.required],
      txt_ruc: ['', Validators.required],
      txt_direccion: ['', Validators.required],
      txt_fecha: ['', Validators.required],
      txt_telefono: ['', Validators.required],
      txt_necesidad: ['', Validators.required],
      txt_funcionario: ['', Validators.required],
      txt_correo: ['', Validators.required],
      tHora_maxina: ['', Validators.required],
      txt_objetivoCompra: ['', Validators.required],
      txt_plazoEntrega: ['', Validators.required],
      txt_vigenciaOferta: ['', Validators.required],
      txt_garantia: ['', Validators.required],
      txt_formaPago: ['', Validators.required],
      txt_metodologiaTrabajo: ['', Validators.required],
      txt_enlace: ['', Validators.required],
      items: this.fb.array([])
    });

    this.addItem();

    // Aquí agregas la lógica
    this.cotizacionForm.get('txt_necesidad')!.valueChanges
      .subscribe(necesidad => {
        const ruc = this.extraerRucDeNecesidad(necesidad);
        this.cotizacionForm.get('txt_ruc')!.setValue(ruc);
      });

    // Tu lógica previa del valueChanges
    this.itemsArray.valueChanges
      .pipe(startWith(this.itemsArray.value))
      .subscribe(() => {
        const arr = this.itemsArray;
        if (arr.length === 0) {
          this.lastQtyPuSet = false;
          return;
        }
        const lastIndex = arr.length - 1;
        const lastGroup = arr.at(lastIndex) as FormGroup;

        const qty = lastGroup.get('int_cantidad')!.value;
        const pu = lastGroup.get('flo_precioUnitario')!.value;
        const bothSet = qty !== null && pu !== null;

        if (bothSet && !this.lastQtyPuSet) {
          this.addItem();
        }
        this.lastQtyPuSet = bothSet;
      });
  }


  // Conveniencia para el template
  get itemsArray(): FormArray {
    return this.cotizacionForm.get('items') as FormArray;
  }

  // Crea el FormGroup para cada fila (sin empujarla aquí)
  private newItemGroup(): FormGroup {
    return this.fb.group({
      txt_cpc: ['', Validators.required],
      txt_unidad: ['', Validators.required],
      txt_especificaciones: ['', Validators.required],
      int_cantidad: [null, Validators.required],
      flo_precioUnitario: [null, Validators.required],
      flo_precioTotal: [{ value: 0, disabled: true }],
      flo_total: [{ value: 0, disabled: true }]
    });
  }

  // Empuja una nueva fila al arreglo
  addItem() {
    this.itemsArray.push(this.newItemGroup());
  }

  removeItem(i: number) {
    this.itemsArray.removeAt(i);
  }

  // Recalcula y actualiza sólo el control flo_total SIN emitir eventos
  // updateTotals(i: number) {
  //   const grp = this.itemsArray.at(i) as FormGroup;
  //   const qty = Number(grp.get('int_cantidad')!.value)        || 0;
  //   const pu  = Number(grp.get('flo_precioUnitario')!.value)  || 0;
  //   grp.patchValue(
  //     { flo_total: qty * pu },
  //     { emitEvent: false },

  //   );
  // }
  updateTotals(i: number) {
    const grp = this.itemsArray.at(i) as FormGroup;
    const qty = Number(grp.get('int_cantidad')!.value) || 0;
    const pu = Number(grp.get('flo_precioUnitario')!.value) || 0;
    const total = qty * pu;

    grp.patchValue({
      flo_precioTotal: total,   // <— actualizamos este
      flo_total: total          // <— y también este
    }, { emitEvent: false });
  }
  
  submit() {
    // 1) Validar el formulario
    if (this.cotizacionForm.invalid) {
      return;
    }

    // 2) Obtener todos los valores, incluyendo los campos disabled
    const raw = this.cotizacionForm.getRawValue();
    const { items: itemsRaw, ...infoPayload } = raw;
    console.log('Payload Información a enviar:', infoPayload);
    console.log('Items a enviar (RAW):', itemsRaw);

    // 3) Crear la información primero
    this.infoSvc.createInformacion(infoPayload).pipe(
      // 4) Con el proforma_id crear todos los ítems
      switchMap(resInfo => {
        const proforma_id = resInfo.proforma_id;
        const calls = itemsRaw.map((it: any) =>
          this.itemSvc.createItem({ ...it, proforma_id })
        );
        return forkJoin(calls);
      })
    ).subscribe({
      next: _ => {
        this.messageService.add({ severity: 'success', summary: 'Éxito', detail: 'Cotización creada', life: 3000 });

        // 5) Resetear el formulario a su estado inicial
        this.cotizacionForm.reset();
        // Limpiar el arreglo de items y volver a crear la primera fila
        this.itemsArray.clear();
        this.addItem();
      },
      error: err => {
        console.error('Error al guardar:', err);
        this.messageService.add({ severity: 'error', summary: 'Error', detail: 'No se pudo guardar la cotización', life: 3000 });
      }
    });
  }


  /** Suma todos los flo_total de cada fila */
  get totalGeneral(): number {
    return (this.cotizacionForm.get('items') as FormArray)
      .controls
      .reduce((acc, ctrl) => {
        const grp = ctrl as FormGroup;
        const val = grp.get('flo_total')?.value;
        return acc + (Number(val) || 0);
      }, 0);
  }

  private extraerRucDeNecesidad(necesidad: string): string {
    if (!necesidad || necesidad.length < 17) return '';
    return necesidad.substr(4, 13);
  }



}
