export class Informacion {
}

// src/app/modelos/informacion.ts

// --- Primero el ItemRead, que usamos dentro de InformacionRead ---
export interface ItemRead {
  items_id:             number;
  txt_cpc:              string;
  txt_unidad:           string;
  txt_especificaciones: string | null;
  int_cantidad:         number;
  flo_precioUnitario:   number;
  flo_precioTotal:      number;
  flo_total:            number;
  proforma_id:          number;
}

// --- Payload para crear una Informacion (no incluye proforma_id ni items) ---
export interface InformacionCreate {
  txt_cliente?:        string;
  txt_ruc?:            string;
  txt_direccion?:      string;
  txt_fecha?:          string;   // o Date, según prefieras
  txt_telefono?:       string;
  txt_necesidad?:      string;
  txt_funcionario?:    string;
  txt_correo?:         string;
  tHora_maxina?:       string;
  txt_objetivoCompra?: string;
  txt_plazoEntrega?:string;
  txt_vigenciaOferta?:string;
  txt_formaPago?:string;
  txt_metodologiaTrabajo?:string;
  txt_garantia?:string;
  txt_enlace?:string;

}

// --- Lo que recibes al leer/crear (incluye proforma_id y el array items) ---
export interface InformacionRead extends InformacionCreate {
  tTimeHora: any;
  dFechaRegistro: any;
  proforma_id: number;
  estado_id:   number;      // <-- añade esto
  estado_name: string;      // <-- y esto
  items:       ItemRead[];
}

/**
 * Respuesta de GET /informaciones/ 
 * (array completo de cabeceras con sus items anidados)
 */
export type InformacionListResponse = InformacionRead[];