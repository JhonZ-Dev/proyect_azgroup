# app/schemas/items.py
from pydantic import BaseModel
from typing import Optional

class ItemBase(BaseModel):
    txt_cpc:              Optional[str] = None
    txt_unidad:           Optional[str] = None
    txt_especificaciones: Optional[str] = None
    int_cantidad:         Optional[int] = None
    flo_precioUnitario:   Optional[float] = None
    flo_precioTotal:      Optional[float] = None
    flo_total:            Optional[float] = None

class ItemCreate(ItemBase):
    proforma_id: int

class ItemRead(ItemBase):
    items_id:    int
    proforma_id: int

    class Config:
        orm_mode = True
