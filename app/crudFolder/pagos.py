#app/crudFolder/pagos.py
from sqlalchemy.orm import Session
from app.models import Pago
from app.schemasFolder.pagos import PagoCreate, PagoUpdate

def get_pago(db: Session, idPagos: int) -> Pago | None:
    return db.query(Pago).filter(Pago.idPagos == idPagos).first()


def get_pagos(db: Session, skip: int = 0, limit: int = 100, username: str | None = None) -> list[Pago]:
    query = db.query(Pago).order_by(Pago.idPagos)
    if username:
        query = query.filter(Pago.txtUsuarioPaga == username)
    return query.offset(skip).limit(limit).all()


def create_pago(db: Session, pago_in: PagoCreate, username: str | None = None) -> Pago:
    data = pago_in.dict()
    if username:
        data["txtUsuarioPaga"] = username
    db_pago = Pago(**data)
    db.add(db_pago)
    db.commit()
    db.refresh(db_pago)
    return db_pago

def update_pago(
    db: Session,
    idPagos: int,
    pago_in: PagoUpdate
) -> Pago | None:
    pago = get_pago(db, idPagos)
    if not pago:
        return None
    for field, value in pago_in.dict().items():
        setattr(pago, field, value)
    db.commit()
    db.refresh(pago)
    return pago

def delete_pago(db: Session, idPagos: int) -> Pago | None:
    pago = get_pago(db, idPagos)
    if pago:
        db.delete(pago)
        db.commit()
    return pago