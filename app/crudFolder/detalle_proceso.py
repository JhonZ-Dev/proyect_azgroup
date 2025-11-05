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

def get_estado_detalle_default_id(db: Session) -> int:
    """
    Devuelve el estado_id por defecto en estado_detalle para las filas nuevas en tb_detalleprocesos.
    Intenta 'REGISTRADO' -> 'CREADO' -> primer estado existente.
    """
    cand = (
        db.query(EstadoDetalle)
          .filter(func.upper(EstadoDetalle.estado).in_(["REGISTRADO", "CREADO"]))
          .order_by(EstadoDetalle.estado.asc())
          .first()
    )
    if cand:
        return cand.estado_id

    any_state = db.query(EstadoDetalle).order_by(EstadoDetalle.estado_id.asc()).first()
    if not any_state:
        # Si no hay estados, algo está mal en catálogo
        raise RuntimeError("No existen registros en estado_detalle.")
    return any_state.estado_id
def upsert_detalle_from_informacion(
    db: Session,
    info,  # objeto Informacion ya cargado
    estado_detalle_id: Optional[int] = None,
):
    """
    Crea o actualiza (por txt_proforma) una fila en tb_detalleprocesos a partir de 'info'.
    No hace commit: lo hace el llamador.
    """
    if not info.txt_numeroProforma:
        raise ValueError("La información no tiene txt_numeroProforma.")

    # Estado del detalle: si no lo pasan, usar default
    if estado_detalle_id is None:
        estado_detalle_id = get_estado_detalle_default_id(db)

    detalle = (
        db.query(DetalleProceso)
          .filter(DetalleProceso.txt_proforma == info.txt_numeroProforma)
          .first()
    )
    if not detalle:
        detalle = DetalleProceso(txt_proforma=info.txt_numeroProforma)
        db.add(detalle)

    # Mapeo que nos pediste:
    # [txt_oferente]            = "DAYANA"
    # [txt_proforma]            = info.txt_numeroProforma  (ya seteado)
    # [txt_fecha_proforma]      = info.txt_fecha
    # [txt_codigo_proceso]      = info.txt_necesidad
    # [txt_entidad_contratante] = info.txt_funcionario
    # [txt_objeto_compra]       = info.txt_objetivoCompra
    # [txt_plazocontractual]    = info.txt_plazoEntrega
    detalle.txt_oferente            = "DAYANA"
    detalle.txt_fecha_proforma      = info.txt_fecha
    detalle.txt_codigo_proceso      = info.txt_necesidad
    detalle.txt_entidad_contratante = info.txt_funcionario
    detalle.txt_objeto_compra       = info.txt_objetivoCompra
    detalle.txt_plazocontractual    = info.txt_plazoEntrega
    detalle.txtUsuarioRegistra      = info.txtUsuarioRegistra

    # Estado del detalle (OJO: es FK a estado_detalle, no a estados)
    detalle.estado_id = estado_detalle_id

    # Si quieres calcular el valor del contrato (opcional):
    try:
        # si relationship items está cargada:
        detalle.int_valor_contrato = sum((it.flo_total or 0) for it in getattr(info, "items", []) or [])
    except Exception:
        # si no está cargado o falla, lo dejamos nulo
        pass

    # No commit aquí
    return detalle
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

