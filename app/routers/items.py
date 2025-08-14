# app/routers/items.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from app import crud
from app.schemasFolder.items import ItemRead, ItemCreate
from app.auth import get_db, require_permission

router = APIRouter(
    prefix="/items",
    tags=["items"]
)

@router.get(
    "/by-informacion/{proforma_id}",
    response_model=List[ItemRead],             # <-- ItemRead
    dependencies=[Depends(require_permission("list"))]
)
def list_items_by_info(
    proforma_id: int,
    db: Session = Depends(get_db)
):
    return crud.get_items_by_informacion(db, proforma_id)

@router.post(
    "/crear-item",
    response_model=ItemRead,                   # <-- ItemRead
    dependencies=[Depends(require_permission("create"))]
)
def create_item(
    item_in: ItemCreate,                       # <-- ItemCreate
    db: Session = Depends(get_db)
):
    return crud.create_item(db, item_in)

# … etc …
@router.get(
  "/{proforma_id}/items/{items_id}",
  response_model=ItemRead,
  dependencies=[Depends(require_permission("list"))]
)
def read_item_by_info(
    proforma_id: int,
    items_id:    int,
    db:          Session = Depends(get_db)
):
    item = crud.get_item_by_informacion_and_id(db, proforma_id, items_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return item