#app/crudFolder/pagos.py
from sqlalchemy.orm import Session
from app.models import Pago
from app.schemasFolder.pagos import PagoCreate, PagoUpdate

def get_pago(db: Session, idPagos: int) -> Pago | None:
    return db.query(Pago).filter(Pago.idPagos == idPagos).first()


def get_pagos(db: Session, skip: int = 0, limit: int = 100) -> list[Pago]:
    return (
        db.query(Pago)
        .order_by(Pago.idPagos)   # <-- Añade esto
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_pago(db: Session, pago_in: PagoCreate) -> Pago:
    db_pago = Pago(**pago_in.dict())
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