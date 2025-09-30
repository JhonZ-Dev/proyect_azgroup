from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field

class ExtractRequest(BaseModel):
    url: HttpUrl = Field(..., description="URL pública del detalle de la necesidad")

class Attachment(BaseModel):
    title: str
    download_url: str

class ItemExtraido(BaseModel):
    cpc: str
    descripcion_corta: str
    descripcion_larga: str
    unidad: str
    cantidad: str

class ExtractedNCData(BaseModel):
    nombre_entidad: Optional[str] = None
    tipo_necesidad: Optional[str] = None
    codigo_necesidad: Optional[str] = None
    estado_necesidad: Optional[str] = None
    objeto_compra: Optional[str] = None
    fecha_publicacion: Optional[str] = None
    fecha_limite: Optional[str] = None
    funcionario_nombre: Optional[str] = None
    funcionario_correo: Optional[str] = None
    lugar_provincia: Optional[str] = None
    lugar_canton: Optional[str] = None
    lugar_parroquia: Optional[str] = None
    lugar_direccion: Optional[str] = None
    anexos: List[Attachment] = []
    raw_title: Optional[str] = None  # por si cambian etiquetas
    items: List[ItemExtraido] = []
