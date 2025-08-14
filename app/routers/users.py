# routers/users.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import crud, schemas
from app.auth import get_db, require_role

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/create_user", response_model=schemas.UserRead, dependencies=[Depends(require_role("admin"))])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)
