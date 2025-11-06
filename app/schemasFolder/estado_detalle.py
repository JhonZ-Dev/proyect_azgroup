# app/schemasFolder/estado_detalle.py
from pydantic import BaseModel

class EstadoRead(BaseModel):
    estado_id:   int
    estado: str

    class Config:
        orm_mode = True

class EstadoDetalleUpdate(BaseModel):
    estado_id: int