# app/schemasFolder/estado.py
from pydantic import BaseModel

class EstadoRead(BaseModel):
    id:   int
    name: str

    class Config:
        orm_mode = True
