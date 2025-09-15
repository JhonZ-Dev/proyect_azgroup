#crudFolder/informacion.py
from datetime import date, datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import Estado, Informacion, Item
from app.schemasFolder.informacion import InformacionCreate
from sqlalchemy.orm import Session, selectinload
# —— CRUD para tb_informacion ——————————————————————————————

def get_informacion(db: Session, proforma_id: int) -> Informacion | None:
    return db.query(Informacion)\
             .filter(Informacion.proforma_id == proforma_id)\
             .first()

def get_informaciones(db: Session, skip: int = 0, limit: int = 100) -> list[Informacion]:
    return db.query(Informacion)\
             .offset(skip)\
             .limit(limit)\
             .all()

# def create_informacion(db: Session, info_in: InformacionCreate) -> Informacion:
#     db_info = Informacion(**info_in.dict())
#     db.add(db_info)
#     db.commit()
#     db.refresh(db_info)
#     return db_info
def create_informacion(db: Session, info_in: InformacionCreate) -> Informacion:
    # 1) Convertir a dict y añadir " DÍAS" a los campos de plazo y vigencia
    data = info_in.dict()
    if data.get("txt_plazoEntrega") is not None:
        data["txt_plazoEntrega"] = f"{data['txt_plazoEntrega']} DÍAS"
    if data.get("txt_vigenciaOferta") is not None:
        data["txt_vigenciaOferta"] = f"{data['txt_vigenciaOferta']} DÍAS"
    if data.get("txt_garantia") is not None:
        data["txt_garantia"] = f"{data['txt_garantia']} MESES"
    
    # 2) Generar el txt_infimaNro
    now = datetime.utcnow()
    # Cuenta cuántas filas ya existen
    total = db.query(func.count(Informacion.proforma_id)).scalar() or 0
    seq = total + 1
    # Formato DD-MM-XXXXXXXXXX
    data["txt_infimaNro"] = f"{now.day:02d}-{now.month:02d}-{seq:010d}"
     # 3) Fijar estado_id a 1 (CREADO) de manera explícita
    data["estado_id"] = 1

    # 2) Crear la instancia de Informacion con los valores procesados
    db_info = Informacion(**data)
    db.add(db_info)
    db.commit()
    db.refresh(db_info)
    return db_info
def update_informacion(
    db: Session,
    proforma_id: int,
    info_in: InformacionCreate
) -> Informacion | None:
    info = db.query(Informacion).filter(Informacion.proforma_id == proforma_id).first()
    if not info:
        return None

    # 1) Convertir a dict y añadir " DÍAS" a los campos de plazo y vigencia
    data = info_in.dict()
    if data.get("txt_plazoEntrega") is not None:
        data["txt_plazoEntrega"] = f"{data['txt_plazoEntrega']} DÍAS"
    if data.get("txt_vigenciaOferta") is not None:
        data["txt_vigenciaOferta"] = f"{data['txt_vigenciaOferta']} DÍAS"
    if data.get("txt_garantia") is not None:
        data["txt_garantia"] = f"{data['txt_garantia']} MESES"
    # 2) Asignar los nuevos valores
    for field, value in data.items():
        setattr(info, field, value)

    db.commit()
    db.refresh(info)
    return info

def delete_informacion(db: Session, proforma_id: int) -> Informacion | None:
    info = get_informacion(db, proforma_id)
    if info:
        db.delete(info)
        db.commit()
    return info


def get_informaciones_with_items(db: Session) -> list[Informacion]:
    """
    Devuelve todas las Informacion, cargando sus items relacionados.
    """
    return (
        db.query(Informacion)
          .options(selectinload(Informacion.items))
          .all()
    )
def get_informacion_with_items_by_id(
    db: Session,
    proforma_id: int
) -> Informacion | None:
    """
    Recupera una única Informacion con todos sus items cargados.
    """
    return (
        db.query(Informacion)
          .options(selectinload(Informacion.items))
          .filter(Informacion.proforma_id == proforma_id)
          .first()
    )


def update_estado_informacion(
    db: Session,
    proforma_id: int,
    estado_id: int
) -> Informacion | None:
    info = db.query(Informacion).filter(Informacion.proforma_id == proforma_id).first()
    if not info:
        return None
    info.estado_id = estado_id
    db.commit()
    db.refresh(info)
    return info

def get_totales_por_estado(db: Session):
    res = (
        db.query(Estado.name.label("estado"), func.count(Informacion.proforma_id).label("total"))
        .outerjoin(Informacion, Informacion.estado_id == Estado.id)
        .group_by(Estado.name)
        .order_by(Estado.name)
        .all()
    )
    return [{"estado": r.estado, "total": r.total} for r in res]


def get_resumen_proformas(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    fecha_ini: date | None = None,
    fecha_fin: date | None = None
):
    # Subquery: total por proforma_id
    sub = (
        db.query(
            Item.proforma_id.label("proforma_id"),
            func.sum(Item.flo_total).label("valor_contrato")
        )
        .group_by(Item.proforma_id)
        .subquery()
    )

    q = (
        db.query(
            Informacion.txtUsuarioRegistra,
            Informacion.txt_infimaNro,
            Informacion.txt_fecha,
            Informacion.txt_necesidad,
            Informacion.txt_cliente,
            Informacion.txt_objetivoCompra,
            sub.c.valor_contrato,
            Informacion.txt_plazoEntrega,
        )
        .join(sub, sub.c.proforma_id == Informacion.proforma_id)   # INNER JOIN
    )

    # Filtros de fecha (opcionales) sobre Informacion.txt_fecha
    if fecha_ini is not None:
        q = q.filter(Informacion.txt_fecha >= fecha_ini)
    if fecha_fin is not None:
        q = q.filter(Informacion.txt_fecha < fecha_fin)

    rows = (
        q.order_by(Informacion.txt_infimaNro)
         .offset(skip)
         .limit(limit)
         .execution_options(stream_results=True)
         .all()
    )

    # Devuelve dicts cómodos
    return [
        {
            "txtUsuarioRegistra": r[0],
            "txt_infimaNro": r[1],
            "txt_fecha": r[2],
            "txt_necesidad": r[3],
            "txt_cliente": r[4],
            "txt_objetivoCompra": r[5],
            "valor_contrato": float(r[6] or 0),
            "txt_plazoEntrega": r[7],
        }
        for r in rows
    ]


def get_reporte_proformas(db: Session):
    from app.models import Informacion, Item  # Ajusta el import a tu estructura
    
    res = (
        db.query(
            Informacion.txtUsuarioRegistra.label('oferente'),
            Informacion.txt_infimaNro.label('proforma'),
            Informacion.txt_fecha.label('fecha_proforma'),
            Informacion.txt_necesidad.label('codigo_proceso'),
            Informacion.txt_cliente.label('entidad_contratante'),
            Informacion.txt_objetivoCompra.label('objeto_compra'),
            func.sum(Item.flo_total).label('valor_contrato'),
            Informacion.txt_plazoEntrega.label('plazo_contractual')
        )
        .join(Item, Informacion.proforma_id == Item.proforma_id)
        .group_by(
            Informacion.txtUsuarioRegistra,
            Informacion.txt_infimaNro,
            Informacion.txt_fecha,
            Informacion.txt_necesidad,
            Informacion.txt_cliente,
            Informacion.txt_objetivoCompra,
            Informacion.txt_plazoEntrega
        )
        .order_by(Informacion.txt_infimaNro)
        .all()
    )
    # Opcional: convertir a lista de dicts
    return [dict(r._mapping) for r in res]