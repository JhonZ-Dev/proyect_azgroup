# app/routers/pagos.py

import json
import os
import shutil
from uuid import uuid4
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Request, UploadFile, status
from typing import List
from fastapi.responses import FileResponse
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
from app.services.receipt_service import generar_comprobante_pdf_weasy
from app.config import SECRET_KEY
from app.utils.sign_link import sign_token, verify_token

router = APIRouter(
    prefix="/pagos",
    tags=["pagos"]
)

@router.get("/listar-pagos", response_model=List[PagosRead])
def list_pagos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    request: Request = None
):
    pagos = get_pagos(db, skip, limit)
    base_url = str(request.base_url).rstrip("/")
    return [PagosRead.from_orm_with_url(p, base_url) for p in pagos]



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
# @router.post(
#     "/crear-pago/email",
#     response_model=PagosRead,
#     status_code=status.HTTP_201_CREATED,
#     dependencies=[Depends(require_permission("create"))]
# )
# def create_pago_email(
#     pago_in: PagoCreate,
#     background_tasks: BackgroundTasks,
#     db: Session = Depends(get_db),
# ):
#     pago = create_pago(db, pago_in)
#     # 1. Leer todos los emails a notificar de la base
#     #emails = [r.emails for r in db.execute("SELECT emails FROM tb_email").fetchall()]
#     emails = [r.emails for r in db.execute(text("SELECT emails FROM tb_email")).fetchall()]
#     print("DEBUG: Emails a notificar:", emails)
#     # 2. Generar cuerpo del correo
#     cuerpo = render_template("pago_realizado.html", {"pago": pago})
#     subject = "Nuevo pago registrado"
#     # 3. Enviar email en background
#     background_tasks.add_task(enviar_email, subject, cuerpo, emails)
#     print("DEBUG: Agregando background task para enviar email")

#     return pago



# @router.post(
#     "/crear-pago/email",
#     response_model=PagosRead,
#     status_code=status.HTTP_201_CREATED,
#     dependencies=[Depends(require_permission("create"))]
# )
# def create_pago_email(
#     pago_in: PagoCreate,
#     background_tasks: BackgroundTasks,
#     request: Request,
#     evidencia: UploadFile = File(None),
#     db: Session = Depends(get_db),
# ):
#     ruta_archivo = None
#     if evidencia:
#         nombre_archivo = f"{uuid4()}_{evidencia.filename}"
#         ruta_carpeta = "uploads/evidencias"
#         os.makedirs(ruta_carpeta, exist_ok=True)
#         ruta_archivo = os.path.join(ruta_carpeta, nombre_archivo)

#         with open(ruta_archivo, "wb") as buffer:
#             shutil.copyfileobj(evidencia.file, buffer)

#         # Guardar solo la ruta relativa
#         pago_in.ruta_evidencia = ruta_archivo
#     pago = create_pago(db, pago_in)

#     base_url = str(request.base_url).rstrip("/")
#     # Token por 24 horas (ajusta si quieres)
#     payload = f"pago:{pago.idPagos}"
#     token = sign_token(SECRET_KEY, payload, ttl_seconds=24*3600)

#     # URL pública con token
#     url_comprobante_publico = f"{base_url}/pagos/publico/{pago.idPagos}/comprobante/{token}"

#     emails = [r.emails for r in db.execute(text("SELECT emails FROM tb_email")).fetchall()]
#     print("DEBUG: Emails a notificar:", emails)

#     # Pasar la URL al template
#     setattr(pago, "urlComprobante", url_comprobante_publico)
#     cuerpo = render_template("pago_realizado.html", {"pago": pago})
#     subject = "Nuevo pago registrado"

#     background_tasks.add_task(enviar_email, subject, cuerpo, emails)
#     print("DEBUG: Email con botón (público, firmado):", url_comprobante_publico)

#     return pago

@router.post(
    "/crear-pago/email",
    response_model=PagosRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("create"))]
)
def create_pago_email(
    pago_in: str = Form(...),  # JSON como texto
    evidencia: UploadFile = File(None),  # Imagen opcional
    background_tasks: BackgroundTasks = None,
    request: Request = None,
    db: Session = Depends(get_db),
):
    # Parsear string JSON a dict
    try:
        data = json.loads(pago_in)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Error al parsear JSON: {str(e)}")

    # Validar con esquema Pydantic
    try:
        pago_schema = PagoCreate(**data)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Datos inválidos: {str(e)}")

    # Guardar imagen si existe
    if evidencia:
        nombre_archivo = f"{uuid4()}_{evidencia.filename}"
        ruta_carpeta = "uploads/evidencias"
        os.makedirs(ruta_carpeta, exist_ok=True)
        ruta_archivo = os.path.join(ruta_carpeta, nombre_archivo)

        with open(ruta_archivo, "wb") as buffer:
            shutil.copyfileobj(evidencia.file, buffer)

        # Guardar la ruta en el schema
        pago_schema.ruta_evidencia = ruta_archivo

    # Guardar el pago en la base
    pago = create_pago(db, pago_schema)

    # Generar URL pública para comprobante
    base_url = str(request.base_url).rstrip("/")
    token = sign_token(SECRET_KEY, f"pago:{pago.idPagos}", ttl_seconds=24 * 3600)
    url_comprobante = f"{base_url}/pagos/publico/{pago.idPagos}/comprobante/{token}"

    # Enviar correo
    #emails = [r.emails for r in db.execute("SELECT emails FROM tb_email").fetchall()]
    emails = [r.emails for r in db.execute(text("SELECT emails FROM tb_email")).fetchall()]
    setattr(pago, "urlComprobante", url_comprobante)
    cuerpo = render_template("pago_realizado.html", {"pago": pago})
    subject = "Nuevo pago registrado"
    background_tasks.add_task(enviar_email, subject, cuerpo, emails)

    return pago
@router.get(
    "/{idPagos}/comprobante",
    response_class=FileResponse,
    dependencies=[Depends(require_permission("list"))]
)
def descargar_comprobante(
    idPagos: int,
    db: Session = Depends(get_db)
):
    pago = get_pago(db, idPagos)
    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")

    # Convertimos el objeto ORM a dict plano (si es necesario)
    pago_dict = {
        "nbIdPago": pago.idPagos,
        "txtMontoPagar": pago.txtMontoPagar,
        "dFechaPago": pago.dFechaPago,
        "txtFormaPago": pago.txtFormaPago,
        "txtUsuarioPaga": pago.txtUsuarioPaga,
        "txtUsuarioRecibe": pago.txtUsuarioRecibe,
        "txtUsuarioCorreo": pago.txtUsuarioCorreo,
        "txtMongoPagarTexto": pago.txtMongoPagarTexto,
        "ruta_evidencia": pago.ruta_evidencia,
    }

    # URL opcional para validación vía QR
    url_validacion = f"https://tu-dominio.com/pagos/{idPagos}/validar"
    empresa_footer = "Empresa S.A. · Av. Siempre Viva 123 · Tel. (000) 000 000"

    pdf_path = generar_comprobante_pdf_weasy(
        pago=pago_dict,
        url_validacion=url_validacion,
        empresa_footer=empresa_footer
    )

    filename = os.path.basename(pdf_path)
    return FileResponse(pdf_path, media_type="application/pdf", filename=filename)


@router.get(
    "/publico/{idPagos}/comprobante/{token}",
    response_class=FileResponse,
)  # <-- SIN require_permission
def descargar_comprobante_publico(
    idPagos: int,
    token: str,
    db: Session = Depends(get_db)
):
    # 1) Validar token
    payload = f"pago:{idPagos}"
    if not verify_token(SECRET_KEY, token, payload):
        raise HTTPException(status_code=401, detail="Link inválido o expirado")

    # 2) Buscar pago
    pago = get_pago(db, idPagos)
    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")

    # 3) Generar/obtener PDF
    pago_dict = {
        "nbIdPago": pago.idPagos,
        "txtMontoPagar": pago.txtMontoPagar,
        "dFechaPago": pago.dFechaPago,
        "txtFormaPago": pago.txtFormaPago,
        "txtUsuarioPaga": pago.txtUsuarioPaga,
        "txtUsuarioRecibe": pago.txtUsuarioRecibe,
        "txtUsuarioCorreo": pago.txtUsuarioCorreo,
        "txtMongoPagarTexto": pago.txtMongoPagarTexto,
        "ruta_evidencia": pago.ruta_evidencia,
    }

    url_validacion = None  # si quieres, arma otra URL pública
    empresa_footer = "Empresa S.A. · Av. Siempre Viva 123 · Tel. (000) 000 000"

    pdf_path = generar_comprobante_pdf_weasy(
        pago=pago_dict,
        url_validacion=url_validacion,
        empresa_footer=empresa_footer
    )
    filename = os.path.basename(pdf_path)
    return FileResponse(pdf_path, media_type="application/pdf", filename=filename)