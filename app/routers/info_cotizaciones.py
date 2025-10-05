from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional


from app.crudFolder import info_cotizaciones as crud
from app.auth import get_db
from app.schemasFolder.info_cotizaciones import InfoCotizacionCreate, InfoCotizacionFull, InfoCotizacionSimple, InfoCotizacionUpdate

router = APIRouter(
    prefix="/info-cotizaciones",
    tags=["Info Cotizaciones"]
)

# 📥 Crear nueva cotización
@router.post("/", response_model=InfoCotizacionSimple, status_code=status.HTTP_201_CREATED)
def create_cotizacion(cotizacion: InfoCotizacionCreate, db: Session = Depends(get_db)):
    return crud.create_info_cotizacion(db, cotizacion)


# 📋 Listar todas las cotizaciones (con paginación)
@router.get("/", response_model=List[InfoCotizacionFull])
def list_cotizaciones(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_all_info_cotizaciones(db, skip=skip, limit=limit)


# 🔍 Obtener cotización por ID
@router.get("/{cotizacionesid}", response_model=InfoCotizacionFull)
def get_cotizacion(cotizacionesid: int, db: Session = Depends(get_db)):
    cot = crud.get_info_cotizacion_by_id(db, cotizacionesid)
    if not cot:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    return cot


# 🔍 Obtener cotizaciones por ID de ítem
@router.get("/item/{items_id}", response_model=List[InfoCotizacionFull])
def get_cotizaciones_por_item(items_id: int, db: Session = Depends(get_db)):
    return crud.get_info_cotizaciones_by_item_id(db, items_id)


# ✏️ Actualizar cotización
@router.put("/{cotizacionesid}", response_model=InfoCotizacionSimple)
def update_cotizacion(cotizacionesid: int, updates: InfoCotizacionUpdate, db: Session = Depends(get_db)):
    try:
        return crud.update_info_cotizacion(db, cotizacionesid, updates)
    except:
        raise HTTPException(status_code=404, detail="Cotización no encontrada o error en actualización")


# 🗑️ Eliminar cotización
@router.delete("/{cotizacionesid}", response_model=InfoCotizacionSimple)
def delete_cotizacion(cotizacionesid: int, db: Session = Depends(get_db)):
    deleted = crud.delete_info_cotizacion(db, cotizacionesid)
    if not deleted:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    return deleted
