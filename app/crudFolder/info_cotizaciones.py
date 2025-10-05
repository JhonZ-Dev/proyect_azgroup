# app/crudFolder/info_cotizaciones.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from app.models import InfoCotizaciones
from app.schemasFolder.info_cotizaciones import InfoCotizacionCreate, InfoCotizacionUpdate



# 📥 Crear una cotización
def create_info_cotizacion(db: Session, cotizacion: InfoCotizacionCreate) -> InfoCotizaciones:
    db_cotizacion = InfoCotizaciones(**cotizacion.dict())
    db.add(db_cotizacion)
    db.commit()
    db.refresh(db_cotizacion)
    return db_cotizacion


# 📋 Obtener todas las cotizaciones
def get_all_info_cotizaciones(db: Session, skip: int = 0, limit: int = 100):
    return db.query(InfoCotizaciones).offset(skip).limit(limit).all()


# 🔍 Obtener una cotización por ID
def get_info_cotizacion_by_id(db: Session, cotizacionesid: int):
    return db.query(InfoCotizaciones).filter(InfoCotizaciones.cotizacionesid == cotizacionesid).first()


# 🔍 Obtener cotizaciones por items_id (opcional)
def get_info_cotizaciones_by_item_id(db: Session, items_id: int):
    return db.query(InfoCotizaciones).filter(InfoCotizaciones.items_id == items_id).all()


# ✏️ Actualizar una cotización
def update_info_cotizacion(db: Session, cotizacionesid: int, updates: InfoCotizacionUpdate):
    db_cotizacion = db.query(InfoCotizaciones).filter(InfoCotizaciones.cotizacionesid == cotizacionesid).first()
    if not db_cotizacion:
        raise NoResultFound(f"Cotización con ID {cotizacionesid} no encontrada.")

    for key, value in updates.dict(exclude_unset=True).items():
        setattr(db_cotizacion, key, value)

    db.commit()
    db.refresh(db_cotizacion)
    return db_cotizacion


# 🗑️ Eliminar una cotización
def delete_info_cotizacion(db: Session, cotizacionesid: int):
    db_cotizacion = db.query(InfoCotizaciones).filter(InfoCotizaciones.cotizacionesid == cotizacionesid).first()
    if not db_cotizacion:
        return None

    db.delete(db_cotizacion)
    db.commit()
    return db_cotizacion
