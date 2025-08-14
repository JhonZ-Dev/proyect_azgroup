# app/routers/roles.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import crud, schemas
from app.auth import get_db, require_role

router = APIRouter(
    prefix="/roles",
    tags=["roles"]
)

@router.post("/", response_model=schemas.Role, dependencies=[Depends(require_role("admin"))])
def create_role(role: schemas.RoleBase, db: Session = Depends(get_db)):
    return crud.create_role(db, role)

@router.get("/", response_model=List[schemas.Role], dependencies=[Depends(require_role("admin"))])
def read_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_roles(db, skip=skip, limit=limit)
