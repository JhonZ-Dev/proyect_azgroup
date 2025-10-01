import { Component, EventEmitter, HostListener, Input, Output } from '@angular/core';
import { ItemsServiceService } from '../servicios/items/items-service.service';
import { InformacionServiceService } from '../servicios/informacion/informacion-service.service';
import { FormArray, FormBuilder, FormControl, FormGroup, FormsModule, NgControl, ReactiveFormsModule, Validators } from '@angular/forms';
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
import { LoginServiceService } from '../servicios/login/login-service.service';
import { UppercaseDirective } from '../../shared/directives/uppercase.directive';
import { FloatLabel } from 'primeng/floatlabel';
import { ProgressSpinnerModule } from 'primeng/progressspinner';

@Component({
  selector: 'app-cotizaciones-component',
  imports: [FormsModule, CommonModule, ReactiveFormsModule, InputTextModule, ButtonModule, InputNumberModule, TextareaModule, InputGroupModule, InputGroupAddonModule, Toast, DialogModule, UppercaseDirective, FloatLabel, ProgressSpinnerModule],
  templateUrl: './cotizaciones-component.component.html',
  styleUrl: './cotizaciones-component.component.css',
  standalone: true,
  providers: [MessageService]
})

export class CotizacionesComponentComponent {

  cotizacionForm!: FormGroup;
  private lastGroupValid = false;
  lastQtyPuSet: any;
  // Arreglo auxiliar para valores de cotizar
  cotizarValores: { puCotizar: number, pt: number, pv: number, diferencia: number }[] = [];
  cargandoEnlace = false;

  private itemCounter = 0;
  // Estado del modal
  especificacionDialogVisible = false;

  // Para saber qué item está editando
  itemEnEdicionIndex: number | null = null;

  constructor(private itemSvc: ItemsServiceService, private infoSvc: InformacionServiceService, private fb: FormBuilder, private messageService: MessageService, private loginSvc: LoginServiceService) { }

  ngOnInit() {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0'); // meses 0-11
    const day = String(today.getDate()).padStart(2, '0');
    const todayStr = `${year}-${month}-${day}`;

    this.cotizacionForm = this.fb.group({
      txt_cliente: ['', Validators.required],
      txt_ruc: ['', Validators.required],
      txt_direccion: ['', Validators.required],
      txt_fecha: [todayStr, Validators.required],
      txt_telefono: ['SN', Validators.required],
      txt_necesidad: ['', Validators.required],
      txt_funcionario: ['', Validators.required],
      txt_correo: ['', Validators.required],
      tHora_maxina: ['', Validators.required],
      txt_objetivoCompra: ['', Validators.required],
      txt_plazoEntrega: ['10', Validators.required],
      txt_vigenciaOferta: ['60', Validators.required],
      txt_garantia: ['12', Validators.required],
      txt_formaPago: ['CONTRA ENTREGA TOTAL DE LOS BIENES', Validators.required],
      txt_metodologiaTrabajo: ['NOS ADHERIMOS A LA METODOLOGIA ESTABLECIDA POR LA ENTIDAD', Validators.required],
      txt_enlace: ['', Validators.required],
      txtUsuarioRegistra: [
        { value: this.loginSvc.getUsername() ?? '', disabled: true },
        Validators.required
      ],
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
          //this.addItem();
        }
        this.lastQtyPuSet = bothSet;
      });
  }


  // Conveniencia para el template
  get itemsArray(): FormArray {
    return this.cotizacionForm.get('items') as FormArray;
  }

  // Crea el FormGroup para cada fila (sin empujarla aquí)
  private newItemGroup(id: number): FormGroup {
    return this.fb.group({
      id: [id],
      txt_cpc: ['', Validators.required],
      txt_unidad: ['UNIDAD', Validators.required],
      txt_especificaciones: ['', Validators.required],
      int_cantidad: [null, Validators.required],
      flo_precioUnitario: [null, Validators.required],
      flo_precioTotal: [{ value: 0, disabled: true }],
      flo_total: [{ value: 0, disabled: true }]
    });
  }

  // Empuja una nueva fila al arreglo
  addItem() {
    //this.itemsArray.push(this.newItemGroup());
    this.itemCounter++;
    this.itemsArray.push(this.newItemGroup(this.itemCounter));
    this.cotizarValores.push({ puCotizar: 0, pt: 0, pv: 0, diferencia: 0 });

    //this.cotizarValores.push({ puCotizar: 0, pt: 0, pv: 0 });
  }

  // removeItem(i: number) {
  //   this.itemsArray.removeAt(i);
  //   this.cotizarValores.splice(i, 1);
  // }
  removeItem(i: number) {
    this.itemsArray.removeAt(i);
    this.cotizarValores.splice(i, 1);

    // 🔹 Recalcular IDs consecutivos según el índice actual
    this.itemsArray.controls.forEach((ctrl, index) => {
      (ctrl as FormGroup).get('id')?.setValue(index + 1);
    });

    // 🔹 Ajustar el contador para que siga en el último ID
    this.itemCounter = this.itemsArray.length;
  }

  updateTotals(i: number) {
    const grp = this.itemsArray.at(i) as FormGroup;
    const qty = Number(grp.get('int_cantidad')!.value) || 0;
    const pu = Number(grp.get('flo_precioUnitario')!.value) || 0;
    const total = qty * pu;

    grp.patchValue({
      flo_precioTotal: total,   // <— actualizamos este
      flo_total: total          // <— y también este
    }, { emitEvent: false });
    // 🔹 recalcular valores de cotizar también
    this.calcularCotizar(i);
  }
  private isItemComplete(item: any): boolean {
    return item.txt_cpc && item.txt_unidad && item.txt_especificaciones &&
      item.int_cantidad !== null && item.flo_precioUnitario !== null &&
      item.flo_precioTotal !== null;
  }


  submit() {
    const raw = this.cotizacionForm.getRawValue();
    let { items: itemsRaw, ...infoPayload } = raw;

    // 🔹 Filtrar ítems incompletos
    itemsRaw = itemsRaw.filter((it: any) => this.isItemComplete(it));

    if (itemsRaw.length === 0) {
      this.messageService.add({
        severity: 'warn',
        summary: 'Advertencia',
        detail: 'Debe ingresar al menos un ítem válido antes de guardar.',
        life: 3000
      });
      return;
    }

    //console.log('Payload Información a enviar:', infoPayload);
    //console.log('Items a enviar (filtrados):', itemsRaw);

    // // 3) Crear la información primero
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

  calcularCotizar(i: number) {
    const item = this.itemsArray.at(i);
    const cantidad = Number(item.get('int_cantidad')?.value) || 0;
    const puBase = Number(item.get('flo_precioUnitario')?.value) || 0;
    const puCotizar = this.cotizarValores[i].puCotizar || 0;

    this.cotizarValores[i].pt = cantidad * puCotizar; // P.T
    this.cotizarValores[i].pv = cantidad * puBase;    // P.V
    this.cotizarValores[i].diferencia = this.cotizarValores[i].pv - this.cotizarValores[i].pt;
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

  /** Suma todos los P.T de la tabla Cotizar */
  get totalPT(): number {
    return this.cotizarValores.reduce((acc, val) => acc + (val.pt || 0), 0);
  }

  /** Suma todos los P.V de la tabla Cotizar */
  get totalPV(): number {
    return this.cotizarValores.reduce((acc, val) => acc + (val.pv || 0), 0);
  }
  /** Suma todas las DIFERENCIAS */
  get totalDiferencia(): number {
    return this.cotizarValores.reduce((acc, val) => acc + (val.diferencia || 0), 0);
  }

  abrirDialogEspecificacion(index: number) {
    this.itemEnEdicionIndex = index;
    this.especificacionDialogVisible = true;
  }

  getItemFormGroup(index: number): FormGroup {
    return this.itemsArray.at(index) as FormGroup;
  }
  cargarDesdeEnlace() {
  const enlace = this.cotizacionForm.get('txt_enlace')?.value?.trim();

  if (!enlace) {
    this.messageService.add({
      severity: 'warn',
      summary: 'Falta el enlace',
      detail: 'Debe ingresar el enlace de la necesidad',
      life: 3000
    });
    return;
  }

  this.cargandoEnlace = true;

  this.infoSvc.extraerDesdeEnlace(enlace).subscribe({
    next: (datosExtraidos) => {
      this.cotizacionForm.patchValue({
        txt_cliente: datosExtraidos.nombre_entidad || '',
        txt_necesidad: datosExtraidos.codigo_necesidad || '',
        txt_objetivoCompra: datosExtraidos.objeto_compra || '',
        txt_fecha: datosExtraidos.fecha_publicacion || '',
        tHora_maxina: datosExtraidos.fecha_limite || '',
        txt_funcionario: datosExtraidos.funcionario_nombre || '',
        txt_correo: datosExtraidos.funcionario_correo || '',
        txt_direccion: `${datosExtraidos.lugar_direccion || ''}, ${datosExtraidos.lugar_parroquia || ''}, ${datosExtraidos.lugar_canton || ''}`
      });

      const necesidad = datosExtraidos.codigo_necesidad;
      if (necesidad?.length >= 17) {
        const ruc = necesidad.substr(4, 13);
        this.cotizacionForm.get('txt_ruc')?.setValue(ruc);
      }

      // 🧩 Cargar ítems si existen
      if (datosExtraidos.items?.length > 0) {
        this.itemsArray.clear();
        this.itemCounter = 0;
        this.cotizarValores = [];

        datosExtraidos.items.forEach((item: any) => {
          this.itemCounter++;
          const grupo = this.fb.group({
            id: [this.itemCounter],
            txt_cpc: [item.cpc || '', Validators.required],
            txt_unidad: [item.unidad || 'UNIDAD', Validators.required],
            txt_especificaciones: [item.descripcion_larga || '', Validators.required],
            int_cantidad: [parseFloat(item.cantidad) || 0, Validators.required],
            flo_precioUnitario: [null, Validators.required],
            flo_precioTotal: [{ value: 0, disabled: true }],
            flo_total: [{ value: 0, disabled: true }]
          });

          this.itemsArray.push(grupo);
          this.cotizarValores.push({ puCotizar: 0, pt: 0, pv: 0, diferencia: 0 });
        });
      }

      this.messageService.add({
        severity: 'success',
        summary: 'Éxito',
        detail: 'Datos extraídos correctamente desde el enlace',
        life: 3000
      });

      this.cargandoEnlace = false;
    },
    error: (err) => {
      console.error('Error al extraer datos:', err);
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: 'No se pudo extraer la información del enlace',
        life: 3000
      });
      this.cargandoEnlace = false;
    }
  });
}


trackByIndex(index: number): number {
  return index;
}


}
