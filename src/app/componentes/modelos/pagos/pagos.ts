export class Pagos {
}

export interface PagosRead {
    txtFormaPago: string;
    txtUsuarioPaga: string;
    txtUsuarioRecibe: string;
    dFechaPago:string;
    tHoraPago: string;
    txtUsuarioCorreo: string;
    txtMontoPagar: number;
    txtMongoPagarTexto: string;
    estado_id: number;
    dFechaRegistro: string;
    tTimeHora:string;
    idPagos: number;
    estado_name:string;
}
export interface PagosCreate {
    txtFormaPago: string;
    txtUsuarioPaga: string;
    txtUsuarioRecibe: string;
    dFechaPago: string;
    tHoraPago: string;
    txtUsuarioCorreo: string;
    txtMontoPagar: number;
    txtMongoPagarTexto: string;
    estado_id: number;
}



