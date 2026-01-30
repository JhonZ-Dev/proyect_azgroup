# app/schemas/items.py
from pydantic import BaseModel
from typing import List, Optional

from app.schemasFolder.info_cotizaciones import InfoCotizacionCreate, InfoCotizacionSimple

class ItemBase(BaseModel):
    txt_cpc:              Optional[str] = None
    txt_unidad:           Optional[str] = None
    txt_especificaciones: Optional[str] = None
    int_cantidad:         Optional[int] = None
    flo_precioUnitario:   Optional[float] = None
    flo_precioTotal:      Optional[float] = None
    flo_total:            Optional[float] = None
    int_orden:            Optional[int] = None
    txt_evidencia:        Optional[str] = None

class ItemCreate(ItemBase):
    proforma_id: int

class ItemCreateIn(BaseModel):
    txt_cpc: str
    txt_unidad: str
    txt_especificaciones: str
    int_cantidad: int
    flo_precioUnitario: Optional[float] = None
    flo_precioTotal: Optional[float] = None
    flo_total: Optional[float] = None
    int_orden: int
    txt_evidencia: Optional[str] = None
    class Config:
        extra = "ignore"  # ignora campos extra si llegan
class ItemRead(ItemBase):
    items_id:    int
    proforma_id: int

    class Config:
        from_attributes = True


class ItemCreateInWithCotizaciones(ItemCreateIn):
    cotizaciones: Optional[List[InfoCotizacionCreate]] = []

class ItemReadWithCotizaciones(ItemRead):
    cotizaciones: List[InfoCotizacionSimple] = []