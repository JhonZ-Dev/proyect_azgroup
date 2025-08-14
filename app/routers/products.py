# routers/products.py
from fastapi import APIRouter, Depends
from typing import List
from app import crud, schemas
from app.auth import get_db, require_permission

router = APIRouter(prefix="/products", tags=["products"])

@router.get(
  "/", response_model=List[schemas.ProductRead],
  dependencies=[Depends(require_permission("list"))]
)
def list_products(skip: int=0, limit:int=100, db=Depends(get_db)):
    return crud.get_products(db, skip, limit)

@router.post(
  "/", response_model=schemas.ProductRead,
  dependencies=[Depends(require_permission("create"))]
)
def create_product(prod_in: schemas.ProductCreate, db=Depends(get_db)):
    return crud.create_product(db, prod_in)
