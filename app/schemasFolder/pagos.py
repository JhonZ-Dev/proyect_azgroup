# app/schemas/pagos.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, time

class PagoBase(BaseModel):
    txtFormaPago: Optional[str] = None
    txtUsuarioPaga: Optional[str] = None
    txtUsuarioRecibe: Optional[str] = None
    dFechaPago: Optional[date] = None
    tHoraPago: Optional[time] = None
    txtUsuarioCorreo: Optional[str] = None
    txtMontoPagar: Optional[float] = None
    txtMongoPagarTexto: Optional[str] = None
    estado_id:Optional[int]   = None
    dFechaRegistro:Optional[date] = None
    tTimeHora:Optional[time] = None
class PagoCreate(PagoBase):
    pass

class PagosRead(PagoBase):
    idPagos: int
    # todos los demás campos heredados de PagoBase    
    estado_name: str
    class Config:
        orm_mode = True
class PagoUpdate(BaseModel):
    estado_id: int