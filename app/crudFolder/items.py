#crudFolder/items.py
from sqlalchemy.orm import Session
from app.models import Item
from app.schemasFolder.items import ItemCreate

# —— CRUD para tb_items ——————————————————————————————————

def get_item(db: Session, items_id: int) -> Item | None:
    return db.query(Item)\
             .filter(Item.items_id == items_id)\
             .first()

def get_items_by_informacion(db: Session, proforma_id: int) -> list[Item]:
    return db.query(Item)\
             .filter(Item.proforma_id == proforma_id)\
             .all()

def create_item(db: Session, item_in: ItemCreate) -> Item:
    db_item = Item(**item_in.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_item(
    db: Session,
    items_id: int,
    item_in: ItemCreate
) -> Item | None:
    item = get_item(db, items_id)
    if not item:
        return None
    for field, value in item_in.dict().items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item

def delete_item(db: Session, items_id: int) -> Item | None:
    item = get_item(db, items_id)
    if item:
        db.delete(item)
        db.commit()
    return item


def get_item_by_informacion_and_id(
    db: Session,
    proforma_id: int,
    items_id: int
) -> Item | None:
    """
    Recupera un único Item que pertenezca a la Informacion dada.
    """
    return (
        db.query(Item)
          .filter(
             Item.proforma_id == proforma_id,
             Item.items_id     == items_id
          )
          .first()
    )