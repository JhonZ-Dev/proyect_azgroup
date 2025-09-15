from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.models import DetalleProceso, EstadoDetalle
from app.schemasFolder.detalle_proceso import (
    DetalleProcesoCreate,
    DetalleProcesoUpdate,
)


# -----------------------------------------
# Util: Uppercase solo para strings
# -----------------------------------------
def _to_uppercase_deep(obj: Any) -> Any:
    if obj is None:
        return obj
    if isinstance(obj, str):
        return obj.upper()
    if isinstance(obj, list):
        return [_to_uppercase_deep(v) for v in obj]
    if isinstance(obj, dict):
        return {k: _to_uppercase_deep(v) for k, v in obj.items()}
    return obj


# -----------------------------------------
# CRUD básico
# -----------------------------------------
def get_detalle(db: Session, detalle_id: int) -> Optional[DetalleProceso]:
    return (
        db.query(DetalleProceso)
        .options(selectinload(DetalleProceso.estado))
        .filter(DetalleProceso.detalle_id == detalle_id)
        .first()
    )


def get_detalles(db: Session, skip: int = 0, limit: int = 100) -> List[DetalleProceso]:
    return (
        db.query(DetalleProceso)
        .options(selectinload(DetalleProceso.estado))
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_details(db: Session) -> list[DetalleProceso]:
    """
    Devuelve todas los detalles procesos, cargando sus items relacionados.
    """
    return (
        db.query(DetalleProceso)
          .options(selectinload(DetalleProceso.estado))
          .all()
    )

def create_detalle(db: Session, detalle_in: DetalleProcesoCreate) -> DetalleProceso:
    # Si quieres normalizar a MAYÚSCULAS (solo strings)
    data = detalle_in.dict()
    data = _to_uppercase_deep(data)

    db_row = DetalleProceso(**data)
    db.add(db_row)
    db.commit()
    db.refresh(db_row)
    return db_row


def update_detalle(
    db: Session, detalle_id: int, detalle_in: DetalleProcesoUpdate
) -> Optional[DetalleProceso]:
    row = db.query(DetalleProceso).filter(DetalleProceso.detalle_id == detalle_id).first()
    if not row:
        return None

    data = detalle_in.dict(exclude_unset=True)
    data = _to_uppercase_deep(data)

    for field, value in data.items():
        setattr(row, field, value)

    db.commit()
    db.refresh(row)
    return row


def delete_detalle(db: Session, detalle_id: int) -> Optional[DetalleProceso]:
    row = db.query(DetalleProceso).filter(DetalleProceso.detalle_id == detalle_id).first()
    if not row:
        return None
    db.delete(row)
    db.commit()
    return row


# -----------------------------------------
# Helpers específicos
# -----------------------------------------
def get_detalles_with_estado(
    db: Session, skip: int = 0, limit: int = 100
) -> List[DetalleProceso]:
    """Lista con eager load del estado."""
    return (
        db.query(DetalleProceso)
        .options(selectinload(DetalleProceso.estado))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_detalle_with_estado_by_id(db: Session, detalle_id: int) -> Optional[DetalleProceso]:
    """Uno por id con el estado cargado."""
    return (
        db.query(DetalleProceso)
        .options(selectinload(DetalleProceso.estado))
        .filter(DetalleProceso.detalle_id == detalle_id)
        .first()
    )


def update_estado_detalle(db: Session, detalle_id: int, estado_id: int) -> Optional[DetalleProceso]:
    """Actualizar solo el estado_id."""
    row = db.query(DetalleProceso).filter(DetalleProceso.detalle_id == detalle_id).first()
    if not row:
        return None
    row.estado_id = estado_id
    db.commit()
    db.refresh(row)
    return row


def get_totales_por_estado_by_detalleproceso(db: Session) -> List[Dict[str, Any]]:
    """
    Conteo de tb_detalleprocesos por estado (nombre).
    Incluye estados sin filas (LEFT JOIN).
    """
    res = (
        db.query(
            EstadoDetalle.estado.label("estado"),
            func.count(DetalleProceso.detalle_id).label("total"),
        )
        .outerjoin(DetalleProceso, DetalleProceso.estado_id == EstadoDetalle.estado_id)
        .group_by(EstadoDetalle.estado)
        .order_by(EstadoDetalle.estado)
        .all()
    )
    return [{"estado": r.estado, "total": r.total} for r in res]

