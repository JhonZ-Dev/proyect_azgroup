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
    ruta_evidencia: Optional[str] = None
class PagoCreate(PagoBase):
    pass

# class PagosRead(PagoBase):
#     idPagos: int
#     # todos los demás campos heredados de PagoBase    
#     estado_name: str
#     class Config:
#         orm_mode = True
class PagosRead(PagoBase):
    idPagos: int
    estado_name: str
    url_evidencia: Optional[str] = None  # ← agregamos este campo virtual

    @staticmethod
    def from_orm_with_url(pago, base_url: str):
        obj = PagosRead.from_orm(pago)
        
        # ✅ Normalizar ruta_evidencia
        if obj.ruta_evidencia:
            obj.ruta_evidencia = obj.ruta_evidencia.replace("\\", "/")

            # ✅ Construir la URL a partir de la ruta
            filename = obj.ruta_evidencia.split("uploads/")[-1]
            obj.url_evidencia = f"{base_url}/uploads/{filename}"

        return obj


    class Config:
        from_attributes  = True

class PagoUpdate(BaseModel):
    estado_id: int