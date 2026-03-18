from datetime import datetime, timedelta
import re
from typing import Optional, List, Dict, Any

from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.models import DetalleProceso, EstadoDetalle, Item
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


def get_detalles(db: Session, skip: int = 0, limit: int = 100, username: str | None = None) -> List[DetalleProceso]:
    query = db.query(DetalleProceso).options(selectinload(DetalleProceso.estado))
    if username:
        query = query.filter(DetalleProceso.txtUsuarioRegistra == username)
    return query.offset(skip).limit(limit).all()

def get_details(db: Session, username: str | None = None) -> list[DetalleProceso]:
    """
    Devuelve todas los detalles procesos, cargando sus items relacionados.
    """
    query = db.query(DetalleProceso).options(selectinload(DetalleProceso.estado)).filter(DetalleProceso.is_active == True)
    if username:
        query = query.filter(DetalleProceso.txtUsuarioRegistra == username)
    return query.all()

def create_detalle(db: Session, detalle_in: DetalleProcesoCreate, username: str | None = None) -> DetalleProceso:
    # Si quieres normalizar a MAYÚSCULAS (solo strings)
    data = detalle_in.dict()
    if username:
        data["txtUsuarioRegistra"] = username
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
    db: Session, skip: int = 0, limit: int = 100, username: str | None = None
) -> List[DetalleProceso]:
    """Lista con eager load del estado."""
    query = db.query(DetalleProceso).options(selectinload(DetalleProceso.estado))
    if username:
        query = query.filter(DetalleProceso.txtUsuarioRegistra == username)
    return query.offset(skip).limit(limit).all()


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
    info,
    estado_detalle_id: Optional[int] = None,
):
    if not info.txt_numeroProforma:
        raise ValueError("La información no tiene txt_numeroProforma.")

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

    # --------- mapeo de campos ----------
    detalle.txt_oferente            = "DAYANA"
    detalle.txt_fecha_proforma      = info.txt_fecha
    detalle.txt_codigo_proceso      = info.txt_necesidad
    detalle.txt_entidad_contratante = info.txt_cliente
    detalle.txt_objeto_compra       = info.txt_objetivoCompra
    detalle.txt_plazocontractual    = info.txt_plazoEntrega
    detalle.txtUsuarioRegistra      = info.txtUsuarioRegistra
    detalle.estado_anterior         = estado_detalle_id
    detalle.estado_id               = 2

    # --------- valor del contrato ---------
    # Suma segura en DB de flo_precioTotal (preferido)
    total = (
        db.query(func.coalesce(func.sum(Item.flo_precioTotal), 0.0))
          .filter(Item.proforma_id == info.proforma_id)
          .scalar()
    )

    # Si quieres fallback a flo_total cuando flo_precioTotal viene nulo:
    if total == 0:
        total_flo_total = (
            db.query(func.coalesce(func.sum(Item.flo_total), 0.0))
              .filter(Item.proforma_id == info.proforma_id)
              .scalar()
        )
        # usa el mayor de ambos por si uno viene vacío
        total = max(float(total or 0), float(total_flo_total or 0))

    # asigna respetando el tipo que uses en la columna
    try:
        detalle.int_valor_contrato = float(total)  # o Decimal(total).quantize(Decimal("0.01"))
    except Exception:
        detalle.int_valor_contrato = None

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


def get_totales_por_estado_by_detalleproceso(db: Session, username: str | None = None) -> List[Dict[str, Any]]:
    """
    Conteo de tb_detalleprocesos por estado (nombre).
    Incluye estados sin filas (LEFT JOIN).
    """
    query = db.query(
            EstadoDetalle.estado.label("estado"),
            func.count(DetalleProceso.detalle_id).label("total"),
        ).outerjoin(DetalleProceso, DetalleProceso.estado_id == EstadoDetalle.estado_id)
    
    if username:
        query = query.filter(DetalleProceso.txtUsuarioRegistra == username)
    
    res = query.group_by(EstadoDetalle.estado).order_by(EstadoDetalle.estado).all()
    return [{"estado": r.estado, "total": r.total} for r in res]

_FECHA_FMT = "%d-%m-%Y"

def _parse_fecha_ddmmyyyy(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    return datetime.strptime(s, _FECHA_FMT)

def _extraer_dias(plazo_str: Optional[str]) -> int:
    """
    '30 DÍAS', '45 dias', '15' -> 30, 45, 15. Si no hay número, 0.
    """
    if not plazo_str:
        return 0
    m = re.search(r"(\d+)", plazo_str)
    return int(m.group(1)) if m else 0

def update_detalle_firma_y_entrega(
    db: Session,
    detalle_id: int,
    txt_firmacontrato: Optional[str] = None,
    txt_fechaentrega: Optional[str] = None,
) -> Optional[DetalleProceso]:
    row = (
        db.query(DetalleProceso)
          .filter(DetalleProceso.detalle_id == detalle_id)
          .first()
    )
    if not row:
        return None

    # 1) Actualiza solo lo que venga en el payload
    if txt_firmacontrato is not None:
        row.txt_firmacontrato = txt_firmacontrato  # puede venir vacío o con fecha válida
    if txt_fechaentrega is not None:
        row.txt_fechaentrega = txt_fechaentrega

    # 2) Recalcular txt_fechafin SOLO si tenemos firma + plazo
    #    (usa lo que haya en row después de actualizar)
    fecha_firma_dt = _parse_fecha_ddmmyyyy(row.txt_firmacontrato) if row.txt_firmacontrato else None
    dias_plazo = _extraer_dias(row.txt_plazocontractual)

    if fecha_firma_dt and dias_plazo > 0:
        fecha_fin_dt = fecha_firma_dt + timedelta(days=dias_plazo)
        row.txt_fechafin = fecha_fin_dt.strftime(_FECHA_FMT)
    # Si no hay datos suficientes, NO tocamos txt_fechafin (se mantiene como estaba)

    # 3) Recalcular días de mora si tenemos fecha fin (ya existente o recién calculada)
    if row.txt_fechafin:
        try:
            fecha_fin_dt = _parse_fecha_ddmmyyyy(row.txt_fechafin)
            hoy = datetime.now()
            row.int_diasmora = max((hoy - fecha_fin_dt).days, 0)
        except Exception:
            # si el formato en DB estuvo mal, no rompas
            pass

    db.commit()
    db.refresh(row)
    return row