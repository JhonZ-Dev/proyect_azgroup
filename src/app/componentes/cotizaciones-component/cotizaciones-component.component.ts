import { Component, EventEmitter, HostListener, Input, Output } from '@angular/core';
import { ItemsServiceService } from '../servicios/items/items-service.service';
import { InformacionServiceService } from '../servicios/informacion/informacion-service.service';
import { FormArray, FormBuilder, FormControl, FormGroup, FormsModule, NgControl, ReactiveFormsModule, Validators } from '@angular/forms';
import { combineLatest, finalize, forkJoin, startWith, switchMap } from 'rxjs';
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
import { SelectModule } from 'primeng/select';
import { UpdateCotizacionesComponent } from "./update-cotizaciones/update-cotizaciones.component";
import { InformacionRead } from '../modelos/informacion/informacion';
import { FormatService } from '../servicios/format.service';

@Component({
  selector: 'app-cotizaciones-component',
  imports: [FormsModule, CommonModule, ReactiveFormsModule, InputTextModule, ButtonModule, InputNumberModule, TextareaModule, InputGroupModule, InputGroupAddonModule, Toast, DialogModule, UppercaseDirective, FloatLabel, ProgressSpinnerModule, SelectModule, UpdateCotizacionesComponent],
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

  ivaOptions = [
    { label: '0', value: 0 },
    { label: '15', value: 15 }
  ];

  private itemCounter = 0;
  // Estado del modal
  especificacionDialogVisible = false;
  evidenciaDialogVisible = false;

  // Para saber qué item está editando
  itemEnEdicionIndex: number | null = null;
  evidenciaEnEdicionIndex: number | null = null;
  cargandoParaEditar = false;

  constructor(
    private itemSvc: ItemsServiceService, 
    private infoSvc: InformacionServiceService, 
    private fb: FormBuilder, 
    private messageService: MessageService, 
    private loginSvc: LoginServiceService,
    public formatService: FormatService
  ) { }

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
      txt_evidencia: [''],
      flo_precioUnitario: [null, Validators.required],
      flo_precioTotal: [{ value: 0, disabled: true }],
      flo_total: [{ value: 0, disabled: true }],
      flo_iva_porcentaje: [15],
      flo_iva_valor: [{ value: 0, disabled: true }]
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

    const pct = Number(grp.get('flo_iva_porcentaje')?.value) || 0;
    const iva = total * (pct / 100);

    grp.patchValue({
      flo_precioTotal: total,   // <— actualizamos este
      flo_total: total,          // <— y también este
      flo_iva_valor: iva
    }, { emitEvent: false });
    // 🔹 recalcular valores de cotizar también
    this.calcularCotizar(i);
  }
  private isItemComplete(item: any): boolean {
    return item.txt_cpc && item.txt_unidad && item.txt_especificaciones &&
      item.int_cantidad !== null && item.flo_precioUnitario !== null &&
      item.flo_precioTotal !== null;
  }

  saving = false;

  submit() {
    if (this.cotizacionForm.invalid) {
      this.messageService.add({
        severity: 'warn',
        summary: 'Formulario incompleto',
        detail: 'Revisa los campos obligatorios.',
        life: 3000,
      });
      return;
    }

    const raw = this.cotizacionForm.getRawValue();
    let { items: itemsRaw, ...infoPayload } = raw;

    // Filtrar ítems incompletos
    itemsRaw = itemsRaw.filter((it: any) => this.isItemComplete(it));
    if (itemsRaw.length === 0) {
      this.messageService.add({
        severity: 'warn',
        summary: 'Advertencia',
        detail: 'Debe ingresar al menos un ítem válido antes de guardar.',
        life: 3000,
      });
      return;
    }

    // Orden explícito para conservar el orden visual del usuario
    itemsRaw = itemsRaw.map((it: any, idx: number) => ({
      ...it,
      int_orden: idx + 1,
    }));

    // Bloquea la UI mientras guarda
    const prevDisabled = this.cotizacionForm.disabled;
    this.saving = true;
    this.cotizacionForm.disable();
    console.log("Info a enviar", infoPayload)
    // this.infoSvc.createInformacion(infoPayload).pipe(
    //   // Solo si la info se crea OK, pasamos a crear ítems
    //   switchMap(resInfo => {
    //     const proforma_id = resInfo.proforma_id;
    //     return forkJoin(
    //       itemsRaw.map((it: any) => this.itemSvc.createItem({ ...it, proforma_id }))
    //     );
    //   }),
    //   finalize(() => {
    //     this.saving = false;
    //     if (!prevDisabled) this.cotizacionForm.enable();
    //   })
    // ).subscribe({
    //   next: _ => {
    //     this.messageService.add({
    //       severity: 'success',
    //       summary: 'Éxito',
    //       detail: 'Cotización creada',
    //       life: 3000
    //     });

    //     // Reset del formulario y reinicio de la primera fila
    //     this.cotizacionForm.reset();
    //     this.itemsArray.clear();
    //     this.addItem();
    //   },
    //   error: err => {
    //     // Usar los mensajes del backend si existen
    //     const backendMsg = err?.error?.detail || err?.error?.message || err?.message;

    //     if (err?.status === 409) {
    //       // txt_necesidad duplicada
    //       this.messageService.add({
    //         severity: 'warn',
    //         summary: 'Registro duplicado',
    //         detail: backendMsg || 'La necesidad ya existe. No se puede crear otra proforma con el mismo código.',
    //         life: 4000
    //       });
    //       return;
    //     }

    //     if (err?.status === 400) {
    //       // Datos inválidos
    //       this.messageService.add({
    //         severity: 'warn',
    //         summary: 'Datos inválidos',
    //         detail: backendMsg || 'Revise los campos enviados.',
    //         life: 4000
    //       });
    //       return;
    //     }

    //     // Otros errores (500, red, etc.)
    //     this.messageService.add({
    //       severity: 'error',
    //       summary: 'Error',
    //       detail: backendMsg || 'No se pudo guardar la cotización.',
    //       life: 4000
    //     });
    //   }
    // });
  }

  // submitFull() {
  //   if (this.cotizacionForm.invalid) {
  //     this.messageService.add({
  //       severity: 'warn',
  //       summary: 'Formulario incompleto',
  //       detail: 'Revisa los campos obligatorios.',
  //       life: 3000,
  //     });
  //     return;
  //   }

  //   const raw = this.cotizacionForm.getRawValue();
  //   let { items: itemsRaw, ...infoPayload } = raw;

  //   // Filtrar ítems incompletos
  //   itemsRaw = itemsRaw.filter((it: any) => this.isItemComplete(it));
  //   if (itemsRaw.length === 0) {
  //     this.messageService.add({
  //       severity: 'warn',
  //       summary: 'Advertencia',
  //       detail: 'Debe ingresar al menos un ítem válido antes de guardar.',
  //       life: 3000,
  //     });
  //     return;
  //   }

  //   // Mapea ítems y agrega int_orden (1..n). OJO: no enviamos el "id" del front.
  //   // const itemsPayload = itemsRaw.map((it: any, idx: number) => ({
  //   //   txt_cpc: it.txt_cpc,
  //   //   txt_unidad: it.txt_unidad,
  //   //   txt_especificaciones: it.txt_especificaciones,
  //   //   int_cantidad: it.int_cantidad,
  //   //   flo_precioUnitario: it.flo_precioUnitario,
  //   //   flo_precioTotal: it.flo_precioTotal,
  //   //   flo_total: it.flo_total,
  //   //   int_orden: idx + 1,
  //   // }));
  //   const itemsPayload = itemsRaw.map((it: any, idx: number) => {
  //     const orden = idx + 1;
  //     const cotizacion = this.cotizarValores[idx] || { puCotizar: 0, pt: 0, diferencia: 0, pv: 0 };

  //     return {
  //       txt_cpc: it.txt_cpc,
  //       txt_unidad: it.txt_unidad,
  //       txt_especificaciones: it.txt_especificaciones,
  //       int_cantidad: it.int_cantidad,
  //       flo_precioUnitario: it.flo_precioUnitario,
  //       flo_precioTotal: it.flo_precioTotal,
  //       flo_total: it.flo_total,
  //       int_orden: orden,
  //       cotizaciones: [
  //         {
  //           flo_precioUnitarioCotizar: cotizacion.puCotizar,
  //           flo_precioTotalCotizar: cotizacion.pt,
  //           flo_diferencia: cotizacion.diferencia,
  //           flo_precioUnitarioBase: it.flo_precioUnitario,
  //           precio_venta: cotizacion.pv,
  //           int_orden: orden,
  //         }
  //       ]
  //     };
  //   });


  //   // Payload único para el endpoint full-create
  //   const payload = {
  //     ...infoPayload,      // incluye txtUsuarioRegistra porque usamos getRawValue()
  //     items: itemsPayload, // 👈 aquí van los ítems con int_orden
  //   };

  //   const prevDisabled = this.cotizacionForm.disabled;
  //   this.saving = true;
  //   this.cotizacionForm.disable();
  //   console.log("payload a enviar", payload)
  //   this.infoSvc.fullCreate(payload).pipe(
  //     finalize(() => {
  //       this.saving = false;
  //       if (!prevDisabled) this.cotizacionForm.enable();
  //     })
  //   ).subscribe({
  //     next: _ => {
  //       this.messageService.add({
  //         severity: 'success',
  //         summary: 'Éxito',
  //         detail: 'Cotización creada',
  //         life: 3000
  //       });

  //       // Reset del formulario y reinicio de la primera fila
  //       this.cotizacionForm.reset();
  //       this.itemsArray.clear();
  //       this.addItem();
  //     },
  //     error: err => {
  //       const backendMsg = err?.error?.detail || err?.error?.message || err?.message;

  //       if (err?.status === 409) {
  //         this.messageService.add({
  //           severity: 'warn',
  //           summary: 'Registro duplicado',
  //           detail: backendMsg || 'La necesidad ya existe. No se puede crear otra proforma con el mismo código.',
  //           life: 4000
  //         });
  //         return;
  //       }

  //       if (err?.status === 400) {
  //         this.messageService.add({
  //           severity: 'warn',
  //           summary: 'Datos inválidos',
  //           detail: backendMsg || 'Revise los campos enviados.',
  //           life: 4000
  //         });
  //         return;
  //       }

  //       this.messageService.add({
  //         severity: 'error',
  //         summary: 'Error',
  //         detail: backendMsg || 'No se pudo guardar la cotización.',
  //         life: 4000
  //       });
  //     }
  //   });
  // }
  //   submitFull() {
  //   if (this.cotizacionForm.invalid) {
  //     this.messageService.add({
  //       severity: 'warn',
  //       summary: 'Formulario incompleto',
  //       detail: 'Revisa los campos obligatorios.',
  //       life: 3000,
  //     });
  //     return;
  //   }

  //   const raw = this.cotizacionForm.getRawValue();
  //   let { items: itemsRaw, ...infoPayload } = raw;

  //   // 🔹 Filtrar ítems incompletos
  //   itemsRaw = itemsRaw.filter((it: any) => this.isItemComplete(it));
  //   if (itemsRaw.length === 0) {
  //     this.messageService.add({
  //       severity: 'warn',
  //       summary: 'Advertencia',
  //       detail: 'Debe ingresar al menos un ítem válido antes de guardar.',
  //       life: 3000,
  //     });
  //     return;
  //   }

  //   // 🔹 Armar payload de items + cotizaciones
  //   const itemsPayload = itemsRaw.map((it: any, idx: number) => {
  //     const orden = idx + 1;
  //     const cotizacion = this.cotizarValores[idx] || { puCotizar: 0, pt: 0, diferencia: 0, pv: 0 };

  //     return {
  //       txt_cpc: it.txt_cpc,
  //       txt_unidad: it.txt_unidad,
  //       txt_especificaciones: it.txt_especificaciones,
  //       int_cantidad: it.int_cantidad,
  //       flo_precioUnitario: it.flo_precioUnitario,
  //       flo_precioTotal: it.flo_precioTotal,
  //       flo_total: it.flo_total,
  //       int_orden: orden,
  //       cotizaciones: [
  //         {
  //           flo_precioUnitarioCotizar: cotizacion.puCotizar,
  //           flo_precioTotalCotizar: cotizacion.pt,
  //           flo_diferencia: cotizacion.diferencia,
  //           flo_precioUnitarioBase: it.flo_precioUnitario,
  //           precio_venta: cotizacion.pv,
  //           int_orden: orden,
  //         }
  //       ]
  //     };
  //   });

  //   // 🔹 Payload final
  //   const payload = {
  //     ...infoPayload,
  //     items: itemsPayload,
  //   };

  //   const prevDisabled = this.cotizacionForm.disabled;
  //   this.saving = true;
  //   this.cotizacionForm.disable();

  //   // 🔹 Si estamos editando -> PUT, si no -> POST
  //   const request$ = this.cargandoParaEditar
  //     ? this.infoSvc.updateInformacionFull(this.cotizacionForm.get('txt_necesidad')!.value, payload)
  //     : this.infoSvc.fullCreate(payload);

  //   request$.pipe(
  //     finalize(() => {
  //       this.saving = false;
  //       if (!prevDisabled) this.cotizacionForm.enable();
  //     })
  //   ).subscribe({
  //     next: () => {
  //       this.messageService.add({
  //         severity: 'success',
  //         summary: 'Éxito',
  //         detail: this.cargandoParaEditar ? 'Cotización actualizada' : 'Cotización creada',
  //         life: 3000
  //       });

  //       if (!this.cargandoParaEditar) {
  //         // Solo limpiar si fue creación
  //         this.cotizacionForm.reset();
  //         this.itemsArray.clear();
  //         this.addItem();
  //       }

  //       // reset del estado de edición
  //       this.cargandoParaEditar = false;
  //     },
  //     error: (err) => {
  //       const backendMsg = err?.error?.detail || err?.error?.message || err?.message;
  //       this.messageService.add({
  //         severity: 'error',
  //         summary: 'Error',
  //         detail: backendMsg || 'No se pudo guardar la cotización.',
  //         life: 4000
  //       });
  //     }
  //   });
  // }
  submitFull() {
    if (this.cotizacionForm.invalid) {
      this.messageService.add({
        severity: 'warn',
        summary: 'Formulario incompleto',
        detail: 'Revisa los campos obligatorios.',
        life: 3000,
      });
      return;
    }

    const raw = this.cotizacionForm.getRawValue();
    let { items: itemsRaw, ...infoPayload } = raw;

    // 🔹 Filtrar ítems incompletos
    itemsRaw = itemsRaw.filter((it: any) => this.isItemComplete(it));
    if (itemsRaw.length === 0) {
      this.messageService.add({
        severity: 'warn',
        summary: 'Advertencia',
        detail: 'Debe ingresar al menos un ítem válido antes de guardar.',
        life: 3000,
      });
      return;
    }

    // 🔹 Armar payload de items + cotizaciones
    const itemsPayload = itemsRaw.map((it: any, idx: number) => {
      const orden = idx + 1;
      const cotizacion = this.cotizarValores[idx] || { puCotizar: 0, pt: 0, diferencia: 0, pv: 0 };

      // ✅ Normalizar txt_evidencia: enviar null si está vacío o solo whitespace
      const txtEvidencia = it.txt_evidencia?.trim() || null;

      return {
        txt_cpc: it.txt_cpc,
        txt_unidad: it.txt_unidad,
        txt_especificaciones: it.txt_especificaciones,
        int_cantidad: it.int_cantidad,
        flo_precioUnitario: it.flo_precioUnitario,
        flo_precioTotal: it.flo_precioTotal,
        flo_total: it.flo_total,
        flo_iva_porcentaje: this.usarFormatoNuevo() ? (it.flo_iva_porcentaje || 0) : 0,
        flo_iva_valor: this.usarFormatoNuevo() ? (it.flo_iva_valor || 0) : 0,
        int_orden: orden,
        txt_evidencia: txtEvidencia,
        cotizaciones: [
          {
            flo_precioUnitarioCotizar: cotizacion.puCotizar,
            flo_precioTotalCotizar: cotizacion.pt,
            flo_diferencia: cotizacion.diferencia,
            flo_precioUnitarioBase: it.flo_precioUnitario,
            precio_venta: cotizacion.pv,
            int_orden: orden,
          }
        ]
      };
    });

    // 🔹 Payload final
    const payload = {
      ...infoPayload,
      items: itemsPayload,
    };

    const prevDisabled = this.cotizacionForm.disabled;
    this.saving = true;
    this.cotizacionForm.disable();

    const request$ = this.cargandoParaEditar
      ? this.infoSvc.updateInformacionFull(this.cotizacionForm.get('txt_necesidad')!.value, payload)
      : this.infoSvc.fullCreate(payload);

    request$.pipe(
      finalize(() => {
        this.saving = false;
        if (!prevDisabled) this.cotizacionForm.enable();
      })
    ).subscribe({
      next: () => {
        this.messageService.add({
          severity: 'success',
          summary: 'Éxito',
          detail: this.cargandoParaEditar ? 'Cotización actualizada' : 'Cotización creada',
          life: 3000
        });

        // 🔹 Reiniciar al estado inicial y volver a modo creación
        this.cargandoParaEditar = false;

        const today = new Date();
        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, '0');
        const day = String(today.getDate()).padStart(2, '0');
        const todayStr = `${year}-${month}-${day}`;

        const valoresFijos = {
          txt_fecha: todayStr,
          txt_telefono: 'SN',
          txt_plazoEntrega: '10',
          txt_vigenciaOferta: '60',
          txt_garantia: '12',
          txt_formaPago: 'CONTRA ENTREGA TOTAL DE LOS BIENES',
          txt_metodologiaTrabajo: 'NOS ADHERIMOS A LA METODOLOGIA ESTABLECIDA POR LA ENTIDAD',
          txtUsuarioRegistra: this.loginSvc.getUsername() ?? ''
        };

        this.cotizacionForm.reset();
        this.cotizacionForm.patchValue(valoresFijos);
        this.itemsArray.clear();
        this.cotizarValores = [];
        this.itemCounter = 0;
        this.addItem();

        // 🔹 volver a modo creación
        this.cargandoParaEditar = false;
      },
      error: (err) => {
        const backendMsg = err?.error?.detail || err?.error?.message || err?.message;

        // 🔹 Manejo específico para duplicados (Conflict 409)
        if (err?.status === 409) {
          this.messageService.add({
            severity: 'warn',
            summary: 'Registro Duplicado',
            detail: backendMsg || 'La necesidad ya existe. No se puede crear otra proforma con el mismo código.',
            life: 5000
          });
          return;
        }

        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: backendMsg || 'No se pudo guardar la cotización.',
          life: 4000
        });
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


  get totalGeneral(): number {
    return (this.cotizacionForm.get('items') as FormArray)
      .controls
      .reduce((acc, ctrl) => {
        const grp = ctrl as FormGroup;
        const val = grp.get('flo_total')?.value;
        const iva = this.usarFormatoNuevo() ? (grp.get('flo_iva_valor')?.value || 0) : 0;
        return acc + (Number(val) || 0) + Number(iva);
      }, 0);
  }

  get totalSubtotal0(): number {
    return (this.cotizacionForm.get('items') as FormArray).controls.reduce((acc, ctrl) => {
      const p = Number(ctrl.get('flo_iva_porcentaje')?.value) || 0;
      const val = Number(ctrl.get('flo_total')?.value) || 0;
      return p === 0 ? acc + val : acc;
    }, 0);
  }

  get totalSubtotal15(): number {
    return (this.cotizacionForm.get('items') as FormArray).controls.reduce((acc, ctrl) => {
      const p = Number(ctrl.get('flo_iva_porcentaje')?.value) || 0;
      const val = Number(ctrl.get('flo_total')?.value) || 0;
      return p === 15 ? acc + val : acc;
    }, 0);
  }

  get totalIva15(): number {
    return (this.cotizacionForm.get('items') as FormArray).controls.reduce((acc, ctrl) => {
      const p = Number(ctrl.get('flo_iva_porcentaje')?.value) || 0;
      const val = Number(ctrl.get('flo_iva_valor')?.value) || 0;
      return p === 15 ? acc + val : acc;
    }, 0);
  }

  esUsuarioJhon(): boolean {
    const user = this.loginSvc.getUsername() || '';
    return user.toLowerCase().includes('jhon');
  }

  usarFormatoNuevo(): boolean {
    return this.esUsuarioJhon() && this.formatService.formatoSeleccionado === 'nuevo';
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
  abrirDialogEvidencia(index: number) {
    this.evidenciaEnEdicionIndex = index;
    this.evidenciaDialogVisible = true;
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
    this.cargandoParaEditar = false; // 🔹 Al cargar desde enlace, nos aseguramos de estar en modo creación

    this.infoSvc.extraerDesdeEnlace(enlace).subscribe({
      next: (datosExtraidos) => {
        this.cotizacionForm.patchValue({
          txt_cliente: datosExtraidos.nombre_entidad || '',
          txt_necesidad: datosExtraidos.codigo_necesidad || '',
          txt_objetivoCompra: datosExtraidos.objeto_compra || '',
          // txt_fecha: datosExtraidos.fecha_publicacion || '',
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
              flo_total: [{ value: 0, disabled: true }],
              flo_iva_porcentaje: [15],
              flo_iva_valor: [{ value: 0, disabled: true }],
              txt_evidencia: ['']
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
        const backendMsg = err?.error?.detail || err?.error?.message || err?.message;

        if (err?.status === 409) {
          this.messageService.add({
            severity: 'warn',
            summary: 'Registro Duplicado',
            detail: backendMsg || 'Ya tienes una proforma registrada para este NIC.',
            life: 5000
          });
        } else {
          this.messageService.add({
            severity: 'error',
            summary: 'Error',
            detail: backendMsg || 'No se pudo extraer la información del enlace',
            life: 3000
          });
        }
        this.cargandoEnlace = false;
      }
    });
  }


  trackByIndex(index: number): number {
    return index;
  }

  cargarCotizacion(data: InformacionRead) {
    if (!data) return; // 🔹 No hacer nada si los datos son nulos
    this.cargandoParaEditar = true; // 👈 esto cambia el botón a "Actualizar"

    // 🔹 Rellena los campos de cabecera
    this.cotizacionForm.patchValue({
      txt_cliente: data.txt_cliente,
      txt_ruc: data.txt_ruc,
      txt_direccion: data.txt_direccion,
      txt_fecha: data.txt_fecha,
      txt_telefono: data.txt_telefono,
      txt_necesidad: data.txt_necesidad,
      txt_funcionario: data.txt_funcionario,
      txt_correo: data.txt_correo,
      tHora_maxina: data.tHora_maxina,
      txt_objetivoCompra: data.txt_objetivoCompra,
      txt_plazoEntrega: data.txt_plazoEntrega,
      txt_vigenciaOferta: data.txt_vigenciaOferta,
      txt_garantia: data.txt_garantia,
      txt_formaPago: data.txt_formaPago,
      txt_metodologiaTrabajo: data.txt_metodologiaTrabajo,
      txt_enlace: data.txt_enlace,
    });

    // 🔹 Limpiar items actuales
    this.itemsArray.clear();
    this.itemCounter = 0;
    this.cotizarValores = [];

    // 🔹 Cargar ítems existentes
    data.items.forEach((item, idx) => {
      this.itemCounter++;
      const grupo = this.fb.group({
        id: [this.itemCounter],
        txt_cpc: [item.txt_cpc, Validators.required],
        txt_unidad: [item.txt_unidad, Validators.required],
        txt_especificaciones: [item.txt_especificaciones, Validators.required],
        int_cantidad: [item.int_cantidad, Validators.required],
        flo_precioUnitario: [item.flo_precioUnitario, Validators.required],
        flo_precioTotal: [item.flo_precioTotal],
        flo_total: [item.flo_total],
        flo_iva_porcentaje: [item.flo_iva_porcentaje || 0],
        flo_iva_valor: [item.flo_iva_valor || 0],
        txt_evidencia: [item.txt_evidencia || ''] // ✅ Agregado para cargar evidencia existente
      });
      this.itemsArray.push(grupo);

      // Si ya tiene cotizaciones, cargamos el primero
      const cot = item.cotizaciones?.[0] || { flo_precioUnitarioCotizar: 0, flo_precioTotalCotizar: 0, precio_venta: 0, flo_diferencia: 0 };
      this.cotizarValores.push({
        puCotizar: cot.flo_precioUnitarioCotizar || 0,
        pt: cot.flo_precioTotalCotizar || 0,
        pv: cot.precio_venta || 0,
        diferencia: cot.flo_diferencia || 0
      });
    });
  }

}
