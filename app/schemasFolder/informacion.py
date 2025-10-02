# app/schemas/informacion.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, time

from app.schemasFolder.items import ItemCreate, ItemCreateIn, ItemRead



class InformacionBase(BaseModel):
    txt_cliente:        Optional[str] = None
    txt_ruc:            Optional[str] = None
    txt_direccion:      Optional[str] = None
    txt_fecha:          Optional[str]  = None
    txt_telefono:       Optional[str] = None
    txt_necesidad:      Optional[str] = None
    txt_funcionario:    Optional[str] = None
    txt_correo:         Optional[str] = None
    tHora_maxina:       Optional[str] = None
    txt_objetivoCompra: Optional[str] = None
    txt_plazoEntrega : Optional[str] = None
    txt_vigenciaOferta   : Optional[str] = None
    txt_garantia : Optional[str] = None
    txt_formaPago : Optional[str] = None
    txt_metodologiaTrabajo : Optional[str] = None
    txt_enlace : Optional[str] = None
    txt_infimaNro : Optional[str] = None
    estado_id:      Optional[int]   = None
    dFechaRegistro:  Optional[date] = None
    tTimeHora:       Optional[time] = None
    txtUsuarioRegistra : Optional[str] = None
    txt_numeroProforma: Optional[str] = None

class InformacionCreate(InformacionBase):
    pass

class InformacionRead(InformacionBase):
    proforma_id: int
    estado_name: str
    dFechaRegistro: date
    tTimeHora:    time
    items:       List[ItemRead] = []

    class Config:
        orm_mode = True
class EstadoUpdate(BaseModel):
    estado_id: int

class EstadoCount(BaseModel):
    estado: str
    total: int

class ProformaReporteOut(BaseModel):
    oferente: Optional[str] = None
    proforma: Optional[str] = None
    fecha_proforma: Optional[str] = None
    codigo_proceso: Optional[str] = None
    entidad_contratante: Optional[str] = None
    objeto_compra: Optional[str] = None
    valor_contrato: Optional[float] = None
    plazo_contractual: Optional[str] = None

class InformacionCreateWithItems(InformacionCreate):
    items: List[ItemCreateIn]