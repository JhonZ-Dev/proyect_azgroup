from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_db, require_permission  # si no usas permisos, quita require_permission
from app.schemasFolder.estado_detalle import EstadoRead
from app.crudFolder.estado_detalle import listar_estados_detalle

router = APIRouter(prefix="/estados-detalle", tags=["EstadoDetalle"])

@router.get("/listar", response_model=list[EstadoRead])
def listar(db: Session = Depends(get_db)):
    return listar_estados_detalle(db)
