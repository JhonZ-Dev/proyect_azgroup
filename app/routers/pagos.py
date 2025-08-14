# app/routers/pagos.py

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from typing import List
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.crudFolder.pagos import (
    get_pago,
    get_pagos,
    create_pago,
    update_pago,
    delete_pago,
)
from app.auth import get_db, require_permission
from app.schemasFolder.pagos import PagoCreate, PagoUpdate, PagosRead
from app.templates.email_templates import pago_realizado_template
from app.utils.email_utils import enviar_email, render_template

router = APIRouter(
    prefix="/pagos",
    tags=["pagos"]
)

@router.get(
    "/listar-pagos",
    response_model=List[PagosRead],
    dependencies=[Depends(require_permission("list"))]
)
def list_pagos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return get_pagos(db, skip, limit)


@router.get(
    "/{idPagos}",
    response_model=PagosRead,
    dependencies=[Depends(require_permission("list"))]
)
def read_pago(
    idPagos: int,
    db: Session = Depends(get_db)
):
    pago = get_pago(db, idPagos)
    if not pago:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pago no encontrado")
    return pago


# @router.post(
#     "/crear-pago",
#     response_model=PagosRead,
#     status_code=status.HTTP_201_CREATED,
#     dependencies=[Depends(require_permission("create"))]
# )
def create_pago_endpoint(
    pago_in: PagoCreate,
    db: Session = Depends(get_db)
):
    return create_pago(db, pago_in)


@router.put(
    "/{idPagos}",
    response_model=PagosRead,
    dependencies=[Depends(require_permission("update"))]
)
def update_pago_endpoint(
    idPagos: int,
    pago_in: PagoUpdate,  
    db: Session = Depends(get_db)
):
    pago = update_pago(db, idPagos, pago_in)
    if not pago:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pago no encontrado")
    return pago

@router.delete(
    "/{idPagos}",
    response_model=PagosRead,
    dependencies=[Depends(require_permission("delete"))]
)
def delete_pago_endpoint(
    idPagos: int,
    db: Session = Depends(get_db)
):
    pago = delete_pago(db, idPagos)
    if not pago:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pago no encontrado")
    return pago

#####POR CORREOS
@router.post(
    "/crear-pago/email",
    response_model=PagosRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("create"))]
)
def create_pago_email(
    pago_in: PagoCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    pago = create_pago(db, pago_in)
    # 1. Leer todos los emails a notificar de la base
    #emails = [r.emails for r in db.execute("SELECT emails FROM tb_email").fetchall()]
    emails = [r.emails for r in db.execute(text("SELECT emails FROM tb_email")).fetchall()]
    print("DEBUG: Emails a notificar:", emails)
    # 2. Generar cuerpo del correo
    cuerpo = render_template("pago_realizado.html", {"pago": pago})
    subject = "Nuevo pago registrado"
    # 3. Enviar email en background
    background_tasks.add_task(enviar_email, subject, cuerpo, emails)
    print("DEBUG: Agregando background task para enviar email")

    return pago