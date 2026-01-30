# app/schemas/info_cotizaciones.py
from pydantic import BaseModel
from typing import Optional

# 🧱 Esquema base
class InfoCotizacionBase(BaseModel):
    flo_precioUnitarioCotizar: Optional[float] = None
    flo_precioTotalCotizar: Optional[float] = None
    flo_diferencia: Optional[float] = None
    flo_precioUnitarioBase: Optional[float] = None
    precio_venta: Optional[float] = None
    items_id: Optional[int] = None
    int_orden: Optional[int] = None


# 📥 Para crear nueva cotización
class InfoCotizacionCreate(InfoCotizacionBase):
    items_id: Optional[int] = None


# 🔁 Para actualizar cotización existente
class InfoCotizacionUpdate(InfoCotizacionBase):
    pass


# 📤 Para mostrar datos de cotización (sin relaciones)
class InfoCotizacionSimple(InfoCotizacionBase):
    cotizacionesid: int

    class Config:
        from_attributes = True


# 📤 Para mostrar con relación al ítem
class ItemSimple(BaseModel):
    items_id: int
    txt_cpc: Optional[str]
    txt_unidad: Optional[str]
    txt_especificaciones: Optional[str]

    class Config:
        from_attributes = True


class InfoCotizacionFull(InfoCotizacionSimple):
    item: Optional[ItemSimple]
