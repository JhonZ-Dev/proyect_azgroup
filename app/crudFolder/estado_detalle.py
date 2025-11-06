from datetime import datetime, timedelta
import re
from typing import Optional, List, Dict, Any

from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload
from app.models import EstadoDetalle


def listar_estados_detalle(db: Session):
    return db.query(EstadoDetalle).order_by(EstadoDetalle.estado.asc()).all()
