# app/routers/informaciones.py
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status, Request
from typing import Any, List
from sqlalchemy.orm import Session
from typing import List, Dict
from app import crud
from app.schemasFolder.informacion import EstadoCount, EstadoUpdate, InformacionCreateWithItems, InformacionRead, InformacionCreate, ProformaReporteOut, PaginatedInformacionRead
from app.auth import get_db, require_permission, get_current_user
from app import models
from app.crudFolder.informacion import create_informacion_con_items, get_informacion_by_necesidad, get_informacion_with_items_by_id, get_informaciones_with_items, get_informaciones_with_items_and_cotizaciones, get_reporte_proformas, update_informacion_con_items
from fastapi.responses import FileResponse
from app.utils.docx_utils import generar_doc_proforma
from app.utils.excel_utils import generar_excel_proforma
from app.utils.pdf_utils import generar_pdf_proforma
import os
from fastapi import BackgroundTasks

router = APIRouter(
    prefix="/informaciones",
    tags=["informaciones"]
)

@router.get(
    "/",
    response_model=List[InformacionRead],        # <-- aquí usas InformacionRead directamente
    dependencies=[Depends(require_permission("list"))]
)
def list_informaciones(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, gt=0, le=1000),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_informaciones(db, skip, limit, username=current_user.username)

# @router.post(
#     "/create-informacion",
#     response_model=InformacionRead,              # <-- y aquí
#     dependencies=[Depends(require_permission("create"))]
# )
# def create_informacion(
#     info_in: InformacionCreate,                  # <-- y aqui InformacionCreate
#     db: Session = Depends(get_db)
# ):
#     return crud.create_informacion(db, info_in)

@router.post(
    "/create-informacion",
    response_model=InformacionRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("create"))],
)
def create_informacion(
    info_in: InformacionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        return crud.create_informacion(db, info_in, username=current_user.username)
    except RuntimeError as e:
        # Duplicada u otra regla de negocio desde el CRUD
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValueError as e:
        # Datos faltantes/invalidos desde el CRUD
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
# … el resto de endpoints igual …

@router.post(
    "/full-create",
    response_model=InformacionRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("create"))],
)
def full_create_informacion(
    payload: InformacionCreateWithItems,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        return create_informacion_con_items(db, payload, username=current_user.username)
    except RuntimeError as e:
        # duplicada u otra regla de negocio
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get(
    "/listar-informaciones",
    response_model=List[InformacionRead],
    dependencies=[Depends(require_permission("list"))]
)
def list_informaciones(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Retorna todas las informaciones con su lista de items anidados.
    """
    return get_informaciones_with_items(db, username=current_user.username)

@router.get(
    "/listar-informaciones-full",
    response_model=PaginatedInformacionRead,
    dependencies=[Depends(require_permission("list"))]
)
def list_informaciones_full(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, gt=0, le=100),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Retorna todas las informaciones con sus items y cotizaciones anidadas de forma paginada.
    """
    items, total = get_informaciones_with_items_and_cotizaciones(db, skip=skip, limit=limit, username=current_user.username)
    
    base_url = str(request.url).split('?')[0]
    
    next_url = None
    if skip + limit < total:
        next_url = f"{base_url}?skip={skip + limit}&limit={limit}"
        
    prev_url = None
    if skip > 0:
        new_skip = max(0, skip - limit)
        prev_url = f"{base_url}?skip={new_skip}&limit={limit}"

    return {
        "count": total,
        "next": next_url,
        "previous": prev_url,
        "results": items
    }
@router.get(
    "/estadisticas-por-estado",
    response_model=List[EstadoCount],
    dependencies=[Depends(require_permission("list"))],
    summary="Resumen de totales por estado de las proformas"
)
def estadisticas_por_estado(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_totales_por_estado(db, username=current_user.username)

@router.get(
    "/resumen",
    response_model=List[Dict[str, Any]],
    dependencies=[Depends(require_permission("list"))],
    summary="Resumen de proformas (agregado por proforma)"
)
def resumen_proformas(
    skip: int = Query(0, ge=0, description="Desplazamiento para paginación"),
    limit: int = Query(100, gt=0, le=1000, description="Tamaño de página"),
    fecha_ini: date | None = Query(None, description="Filtrar desde esta fecha (txt_fecha)"),
    fecha_fin: date | None = Query(None, description="Filtrar hasta esta fecha (txt_fecha, exclusivo)"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    rows = crud.get_resumen_proformas(db=db, skip=skip, limit=limit, fecha_ini=fecha_ini, fecha_fin=fecha_fin, username=current_user.username)
    return rows


@router.get(
    "/by-necesidad/{codigo}",
    response_model=InformacionRead,
    dependencies=[Depends(require_permission("list"))]
)
def get_by_necesidad(
    codigo: str, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    res = get_informacion_by_necesidad(db, codigo, username=current_user.username)
    if not res:
        raise HTTPException(status_code=404, detail="Proforma no encontrada")
    return res


@router.put(
    "/update-full/{codigo}",
    response_model=InformacionRead,
    dependencies=[Depends(require_permission("update"))]
)
def update_full_informacion(
    codigo: str,
    payload: InformacionCreateWithItems,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        return update_informacion_con_items(db, codigo, payload, username=current_user.username)
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
@router.get(
    "/reporte/proformas",
    response_model=List[ProformaReporteOut],
    dependencies=[Depends(require_permission("list"))]
)
def reporte_proformas(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return get_reporte_proformas(db, username=current_user.username)
@router.get(
    "/{proforma_id}",
    response_model=InformacionRead,
    dependencies=[Depends(require_permission("list"))]
)
def read_informacion(
    proforma_id: int,
    db: Session = Depends(get_db)
):
    info = get_informacion_with_items_by_id(db, proforma_id)
    if not info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Información no encontrada"
        )
    return info

@router.patch(
    "/{proforma_id}/estado",
    response_model=InformacionRead,
    summary="Actualiza solo el estado de una cotización"
)
def patch_estado(
    proforma_id: int,
    payload: EstadoUpdate,
    db: Session = Depends(get_db)
):
    print("Payload recibido:", payload)
    updated = crud.update_estado_informacion(db, proforma_id, payload.estado_id)
    print("Después de update, estado_id en Python:", updated.estado_id)
    # opcional: vuelve a leer directamente de la BD
    fresh = crud.get_informacion(db, proforma_id)
    print("Estado real en DB:", fresh.estado_id)
    if not updated:
        raise HTTPException(404, "Cotización no encontrada")
    return updated

@router.get(
    "/descargar-proforma/{proforma_id}",
    summary="Descarga el archivo Word con la proforma y sus ítems"
)
def descargar_proforma(
    proforma_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    info = get_informacion_with_items_by_id(db, proforma_id)
    if not info:
        raise HTTPException(404, "Información no encontrada")

    nombre_limpio = info.txt_necesidad.replace('-', '_')
    nombre_archivo = f"Proforma_{nombre_limpio}.docx"
    # Plantilla personalizada por usuario
    # __file__ es .../app/routers/informacion.py
    # Vamos 3 niveles arriba para llegar a la raíz del proyecto
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    base_template = os.path.join(project_root, "app", "utils", "plantilla.docx")
    user_template = os.path.join(project_root, "uploads", "templates", current_user.username, "plantilla.docx")
    
    print(f"DEBUG: Descargando Word para usuario: {current_user.username}")
    print(f"DEBUG: Buscando plantilla en: {user_template}")
    print(f"DEBUG: Existe? {os.path.exists(user_template)}")
    
    final_template = user_template if os.path.exists(user_template) else base_template

    archivo_path = generar_doc_proforma(
        data={
        "txt_cliente": info.txt_cliente,
        "txt_ruc": info.txt_ruc,
        "txt_direccion": info.txt_direccion,
        "txt_fecha": str(info.txt_fecha),
        "txt_telefono": info.txt_telefono,
        "txt_necesidad": info.txt_necesidad,
        "txt_funcionario": info.txt_funcionario,
        "txt_correo": info.txt_correo,
        "tHora_maxina": info.tHora_maxina,
        "txt_objetivoCompra": info.txt_objetivoCompra,
        "txt_plazoEntrega": info.txt_plazoEntrega,
        "txt_vigenciaOferta": info.txt_vigenciaOferta,
        "txt_garantia": info.txt_garantia,
        "txt_formaPago": info.txt_formaPago,
        "txt_metodologiaTrabajo": info.txt_metodologiaTrabajo,
        "txt_enlace": info.txt_enlace,
        "txt_infimaNro": info.txt_infimaNro,
        "txt_numeroProforma":info.txt_numeroProforma,
        "txtUsuarioRegistra": info.txtUsuarioRegistra,
        "items": [
            {
                "txt_cpc": item.txt_cpc,
                "txt_unidad": item.txt_unidad,
                "txt_especificaciones": item.txt_especificaciones,
                "int_cantidad": item.int_cantidad,
                "flo_precioUnitario": item.flo_precioUnitario,
                "flo_precioTotal": item.flo_precioTotal,
                "flo_iva_porcentaje": getattr(item, 'flo_iva_porcentaje', 0.0),
                "flo_iva_valor": getattr(item, 'flo_iva_valor', 0.0),
            }
            for item in info.items
        ]
    }, 
    plantilla_path=final_template,
    archivo_salida=nombre_archivo,
    full_name=current_user.full_name,
    job_title=current_user.job_title,
    ruc=current_user.ruc
    )

    background_tasks.add_task(os.remove, archivo_path)

    # 🔥 Generamos el header manual
    headers = {
        "Content-Disposition": f'attachment; filename="{nombre_archivo}"'
    }

    with open(archivo_path, "rb") as f:
        content = f.read()

    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers,
        background=background_tasks
    )

#####si se quiere hacer que solo usuarios autenticados con permisos exportToWord

# @router.get(
#     "/descargar-proforma/{proforma_id}",
#     response_class=FileResponse,
#     summary="Descarga el archivo Word con la proforma y sus ítems",
#     dependencies=[Depends(require_permission("exportToWord"))]
# )
# def descargar_proforma(
#     proforma_id: int,
#     db: Session = Depends(get_db)
# ):
#     info = get_informacion_with_items_by_id(db, proforma_id)
#     if not info:
#         raise HTTPException(404, "Información no encontrada")

#     # Convierte info a dict (usa .dict() si es pydantic, o crea manual si es ORM)
#     if hasattr(info, 'dict'):
#         data = info.dict()
#     else:
#         # Si info es modelo ORM, conviértelo tú mismo
#         data = {
#             "txt_cliente": info.txt_cliente,
#             "txt_ruc": info.txt_ruc,
#             "txt_direccion": info.txt_direccion,
#             "txt_fecha": str(info.txt_fecha),
#             "txt_telefono": info.txt_telefono,
#             "txt_necesidad": info.txt_necesidad,
#             "txt_funcionario": info.txt_funcionario,
#             "txt_correo": info.txt_correo,
#             "tHora_maxina": info.tHora_maxina,
#             "txt_objetivoCompra": info.txt_objetivoCompra,
#             "txt_plazoEntrega": info.txt_plazoEntrega,
#             "txt_vigenciaOferta": info.txt_vigenciaOferta,
#             "txt_garantia": info.txt_garantia,
#             "txt_formaPago": info.txt_formaPago,
#             "txt_metodologiaTrabajo": info.txt_metodologiaTrabajo,
#             "txt_enlace": info.txt_enlace,
#             "items": [
#                 {
#                     "txt_cpc": item.txt_cpc,
#                     "txt_unidad": item.txt_unidad,
#                     "txt_especificaciones": item.txt_especificaciones,
#                     "int_cantidad": item.int_cantidad,
#                     "flo_precioUnitario": item.flo_precioUnitario,
#                     "flo_precioTotal": item.flo_precioTotal,
#                 }
#                 for item in info.items
#             ]
#         }
#     archivo = generar_doc_proforma(data)
#     return FileResponse(archivo, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename=archivo)
@router.get(
    "/descargar-pdf/{proforma_id}",
    response_class=FileResponse,
    summary="Descarga el archivo PDF de la proforma"
)
def descargar_pdf(
    proforma_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    info = get_informacion_with_items_by_id(db, proforma_id)
    if not info:
        raise HTTPException(404, "Información no encontrada")

    # --- Convierte el modelo ORM a dict igual que antes ---
    data = {
        "txt_cliente": info.txt_cliente,
        "txt_ruc": info.txt_ruc,
        "txt_direccion": info.txt_direccion,
        "txt_fecha": str(info.txt_fecha),
        "txt_telefono": info.txt_telefono,
        "txt_necesidad": info.txt_necesidad,
        "txt_funcionario": info.txt_funcionario,
        "txt_correo": info.txt_correo,
        "tHora_maxina": info.tHora_maxina,
        "txt_objetivoCompra": info.txt_objetivoCompra,
        "txt_plazoEntrega": info.txt_plazoEntrega,
        "txt_vigenciaOferta": info.txt_vigenciaOferta,
        "txt_garantia": info.txt_garantia,
        "txt_formaPago": info.txt_formaPago,
        "txt_metodologiaTrabajo": info.txt_metodologiaTrabajo,
        "txt_enlace": info.txt_enlace,
        "txt_infimaNro": info.txt_infimaNro,
        "txt_numeroProforma":info.txt_numeroProforma,
        "txtUsuarioRegistra": info.txtUsuarioRegistra,
        "items": [
            {
                "txt_cpc": item.txt_cpc,
                "txt_unidad": item.txt_unidad,
                "txt_especificaciones": item.txt_especificaciones,
                "int_cantidad": item.int_cantidad,
                "flo_precioUnitario": item.flo_precioUnitario,
                "flo_precioTotal": item.flo_precioTotal,
                "flo_iva_porcentaje": getattr(item, 'flo_iva_porcentaje', 0.0),
                "flo_iva_valor": getattr(item, 'flo_iva_valor', 0.0),
            }
            for item in info.items
        ]
    }
    output_filename = f"Proforma{info.txt_necesidad}.pdf"
    
    # Membrete personalizado por usuario
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    base_membrete = os.path.join(project_root, "app", "utils", "fondomembretada.jpg")
    
    # Intentar con .jpg y .jpeg
    user_membrete_jpg = os.path.join(project_root, "uploads", "templates", current_user.username, "fondomembretada.jpg")
    user_membrete_jpeg = os.path.join(project_root, "uploads", "templates", current_user.username, "fondomembretada.jpeg")
    
    final_membrete = base_membrete
    if os.path.exists(user_membrete_jpg):
        final_membrete = user_membrete_jpg
    elif os.path.exists(user_membrete_jpeg):
        final_membrete = user_membrete_jpeg

    print(f"DEBUG: Descargando PDF para usuario: {current_user.username}")
    print(f"DEBUG: Final membrete: {final_membrete}")
    print(f"DEBUG: ¿Es personalizado? {final_membrete != base_membrete}")
    
    archivo = generar_pdf_proforma(
        data, 
        membrete_path=final_membrete,
        full_name=current_user.full_name,
        job_title=current_user.job_title,
        ruc=current_user.ruc
    )
    background_tasks.add_task(os.remove, archivo)
    return FileResponse(
        archivo,
        media_type="application/pdf",
        filename=os.path.basename(archivo),
        background=background_tasks
    )

@router.get(
    "/descargar-excel/{proforma_id}",
    response_class=FileResponse,
    summary="Descarga el archivo Excel de la proforma"
)
def descargar_excel(
    proforma_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    info = get_informacion_with_items_by_id(db, proforma_id)
    if not info:
        raise HTTPException(404, "Información no encontrada")

    # Reusa tu lógica de conversión
    data = {
        "txt_cliente": info.txt_cliente,
        "txt_ruc": info.txt_ruc,
        "txt_direccion": info.txt_direccion,
        "txt_fecha": str(info.txt_fecha),
        "txt_telefono": info.txt_telefono,
        "txt_necesidad": info.txt_necesidad,
        "txt_funcionario": info.txt_funcionario,
        "txt_correo": info.txt_correo,
        "tHora_maxina": info.tHora_maxina,
        "txt_objetivoCompra": info.txt_objetivoCompra,
        "txt_plazoEntrega": info.txt_plazoEntrega,
        "txt_vigenciaOferta": info.txt_vigenciaOferta,
        "txt_garantia": info.txt_garantia,
        "txt_formaPago": info.txt_formaPago,
        "txt_metodologiaTrabajo": info.txt_metodologiaTrabajo,
        "txt_enlace": info.txt_enlace,
        "txt_infimaNro": info.txt_infimaNro,
        "txt_numeroProforma":info.txt_numeroProforma,
        "items": [
            {
                "txt_cpc": item.txt_cpc,
                "txt_unidad": item.txt_unidad,
                "txt_especificaciones": item.txt_especificaciones,
                "int_cantidad": item.int_cantidad,
                "flo_precioUnitario": item.flo_precioUnitario,
                "flo_precioTotal": item.flo_precioTotal,
                "flo_iva_porcentaje": getattr(item, 'flo_iva_porcentaje', 0.0),
                "flo_iva_valor": getattr(item, 'flo_iva_valor', 0.0),
            }
            for item in info.items
        ]
    }
    # Plantilla Excel personalizada
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    base_excel = os.path.join(project_root, "app", "utils", "template.xlsx")
    user_excel_v2 = os.path.join(project_root, "uploads", "templates", current_user.username, "template_v2_iva.xlsx")
    user_excel = os.path.join(project_root, "uploads", "templates", current_user.username, "template.xlsx")
    
    if os.path.exists(user_excel_v2):
        final_excel = user_excel_v2
    elif os.path.exists(user_excel):
        final_excel = user_excel
    else:
        final_excel = base_excel

    archivo = generar_excel_proforma(data, template_path=final_excel)
    nombre = f"Proforma_{info.txt_necesidad}.xlsx"
    # Eliminar archivo después de enviar
    background_tasks.add_task(os.remove, archivo)
    return FileResponse(archivo, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=nombre,background=background_tasks)

