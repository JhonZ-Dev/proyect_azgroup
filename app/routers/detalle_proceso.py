from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_db, require_permission, get_current_user
from app import models
from app.crudFolder import detalle_proceso as crud
from app.schemasFolder.detalle_proceso import (
    DetalleProcesoFirmaEntregaUpdate,
    DetalleProcesoRead,
    DetalleProcesoCreate,
    DetalleProcesoUpdate,
)
from app.crudFolder.detalle_proceso import get_details, update_detalle_firma_y_entrega
from app.models import DetalleProceso, EstadoDetalle
from app.schemasFolder.estado_detalle import EstadoDetalleUpdate

router = APIRouter(
    prefix="/detalle-procesos",
    tags=["detalle_procesos"]
)

# ---- Schema simple para el endpoint de totales ----
class TotalesPorEstado(BaseModel):
    estado: str
    total: int


# ====================== LISTAR ======================
@router.get(
    "/",
    response_model=List[DetalleProcesoRead],
    dependencies=[Depends(require_permission("list"))]
)
def list_detalles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, gt=0, le=1000),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_detalles(db, skip=skip, limit=limit, username=current_user.username)

@router.get(
    "/listar-detallesprocesos",
    response_model=List[DetalleProcesoRead],
    dependencies=[Depends(require_permission("list"))]
)
def list_details(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Retorna todas las informaciones con su lista de items anidados.
    """
    return get_details(db, username=current_user.username)
# ====================== OBTENER POR ID ======================
@router.get(
    "/{detalle_id}",
    response_model=DetalleProcesoRead,
    dependencies=[Depends(require_permission("read"))]
)
def get_detalle(
    detalle_id: int,
    db: Session = Depends(get_db)
):
    row = crud.get_detalle(db, detalle_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Detalle no encontrado")
    return row


# ====================== CREAR ======================
@router.post(
    "/",
    response_model=DetalleProcesoRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("create"))]
)
def create_detalle(
    payload: DetalleProcesoCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # valida estado_id existente
    estado = db.query(EstadoDetalle).filter(EstadoDetalle.estado_id == payload.estado_id).first()
    if not estado:
        raise HTTPException(status_code=400, detail="estado_id inválido")

    row = crud.create_detalle(db, payload, username=current_user.username)
    return row


# ====================== ACTUALIZAR ======================
@router.put(
    "/{detalle_id}",
    response_model=DetalleProcesoRead,
    dependencies=[Depends(require_permission("update"))]
)
def update_detalle(
    detalle_id: int,
    payload: DetalleProcesoUpdate,
    db: Session = Depends(get_db)
):
    # si viene estado_id, valida que exista
    if payload.estado_id is not None:
        exists = db.query(EstadoDetalle).filter(EstadoDetalle.estado_id == payload.estado_id).first()
        if not exists:
            raise HTTPException(status_code=400, detail="estado_id inválido")

    row = crud.update_detalle(db, detalle_id, payload)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Detalle no encontrado")
    return row


# ====================== ELIMINAR ======================
@router.delete(
    "/{detalle_id}",
    response_model=DetalleProcesoRead,
    dependencies=[Depends(require_permission("delete"))]
)
def delete_detalle(
    detalle_id: int,
    db: Session = Depends(get_db)
):
    row = crud.delete_detalle(db, detalle_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Detalle no encontrado")
    return row


# ====================== ACTUALIZAR SOLO ESTADO ======================
@router.patch(
    "/{detalle_id}/estado/{estado_id}",
    response_model=DetalleProcesoRead,
    dependencies=[Depends(require_permission("update"))]
)
def set_estado_detalle(
    detalle_id: int,
    estado_id: int,
    db: Session = Depends(get_db)
):
    exists = db.query(EstadoDetalle).filter(EstadoDetalle.estado_id == estado_id).first()
    if not exists:
        raise HTTPException(status_code=400, detail="estado_id inválido")

    row = crud.update_estado_detalle(db, detalle_id, estado_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Detalle no encontrado")
    return row


# ====================== TOTALES POR ESTADO ======================
@router.get(
    "/totales/por-estado",
    response_model=List[TotalesPorEstado],
    dependencies=[Depends(require_permission("list"))]
)
def totales_por_estado(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_totales_por_estado_by_detalleproceso(db, username=current_user.username)


@router.put("/{detalle_id}/firma-entrega", response_model=DetalleProcesoRead)
def actualizar_firma_entrega(
    detalle_id: int,
    payload: DetalleProcesoFirmaEntregaUpdate,
    db: Session = Depends(get_db),
):
    row = crud.update_detalle_firma_y_entrega(
        db=db,
        detalle_id=detalle_id,
        txt_firmacontrato=payload.txt_firmacontrato,
        txt_fechaentrega=payload.txt_fechaentrega,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Detalle no encontrado")
    return row



#*====================== ACTUALIZAR ESTADO ======================*#
@router.put("/{detalle_id}/estado", response_model=DetalleProcesoRead)
def actualizar_estado_detalle(detalle_id: int, body: EstadoDetalleUpdate, db: Session = Depends(get_db)):
    row = db.query(DetalleProceso).filter(DetalleProceso.detalle_id == detalle_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Detalle no encontrado")

    estado_anterior = row.estado_id
    row.estado_id = body.estado_id
    row.estado_anterior = estado_anterior
    db.commit()
    db.refresh(row)
    return row