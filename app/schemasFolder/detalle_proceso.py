# app/schemasFolder/detalle_proceso.py
from typing import Optional
from datetime import date, time
from pydantic import BaseModel
from app.schemasFolder.estado_detalle import EstadoRead


# --- Base: campos comunes para create/update ---
class DetalleProcesoBase(BaseModel):
    txt_oferente: Optional[str] = None
    txt_proforma: Optional[str] = None
    txt_fecha_proforma: Optional[str] = None
    txt_codigo_proceso: Optional[str] = None
    txt_entidad_contratante: Optional[str] = None
    txt_objeto_compra: Optional[str] = None
    int_valor_contrato: Optional[int] = None
    txt_plazocontractual: Optional[str] = None
    txt_firmacontrato: Optional[str] = None
    txt_fechafin: Optional[str] = None
    txt_fechaentrega: Optional[str] = None
    int_diasmora: Optional[int] = None
    txtUsuarioRegistra: Optional[str] = None
    # estado_id requerido para crear (lo dejamos aquí y en Create)
    estado_id: Optional[int] = None
    estado_anterior   : Optional[int] = None
    is_active: bool


# --- Create: lo que necesitas para insertar ---
class DetalleProcesoCreate(DetalleProcesoBase):
    estado_id: int  # requerido al crear


# --- Update: todo opcional ---
class DetalleProcesoUpdate(BaseModel):
    txt_oferente: Optional[str] = None
    txt_proforma: Optional[str] = None
    txt_fecha_proforma: Optional[str] = None
    txt_codigo_proceso: Optional[str] = None
    txt_entidad_contratante: Optional[str] = None
    txt_objeto_compra: Optional[str] = None
    int_valor_contrato: Optional[int] = None
    txt_plazocontractual: Optional[str] = None
    txt_firmacontrato: Optional[str] = None
    txt_fechafin: Optional[str] = None
    txt_fechaentrega: Optional[str] = None
    int_diasmora: Optional[int] = None
    txtUsuarioRegistra: Optional[str] = None
    estado_id: Optional[int] = None
    is_active: bool

# --- Read: lo que devuelves al cliente ---
class DetalleProcesoRead(BaseModel):
    detalle_id: int
    txt_oferente: Optional[str] = None
    txt_proforma: Optional[str] = None
    txt_fecha_proforma: Optional[str] = None
    txt_codigo_proceso: Optional[str] = None
    txt_entidad_contratante: Optional[str] = None
    txt_objeto_compra: Optional[str] = None
    int_valor_contrato: Optional[float] = None
    txt_plazocontractual: Optional[str] = None
    txt_firmacontrato: Optional[str] = None
    txt_fechafin: Optional[str] = None
    txt_fechaentrega: Optional[str] = None
    int_diasmora: Optional[int] = None
    txtUsuarioRegistra: Optional[str] = None
    dFechaRegistro: date
    tTimeHora: time
    estado_id: Optional[int] = None 
    estado_name:  Optional[str] = None                 # viene de la @property del modelo
    estado: Optional[EstadoRead] = None  # anidado si quieres enviar el objeto
    estado_anterior   : Optional[int] = None
    is_active: bool
    class Config:
        from_attributes = True


class DetalleProcesoFirmaEntregaUpdate(BaseModel):
    txt_firmacontrato: Optional[str] = None  # "dd-mm-yyyy"
    txt_fechaentrega: Optional[str] = None   # "dd-mm-yyyy"