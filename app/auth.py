# auth.py
from datetime import datetime, timedelta
from jose import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app import crud, models, config
from app.database import SessionLocal
from app.crud import pwd_context

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def authenticate_user(db: Session, username: str, password: str):
    user = crud.get_user(db, username)
    if not user or not pwd_context.verify(password, user.hashed_password):
        return False
    return user

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autorizado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username: str = payload.get("sub")
        roles: list = payload.get("roles", [])
        if username is None:
            raise credentials_exception
    except:
        raise credentials_exception
    user = crud.get_user(db, username)
    if not user:
        raise credentials_exception
    return user

def require_role(role_name: str):
    def role_checker(user: models.User = Depends(get_current_user)):
        if role_name not in [r.name for r in user.roles]:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No tienes este permiso")
        return user
    return role_checker

def require_permission(perm_name: str):
    def checker(
        current_user: models.User = Depends(get_current_user),
        db: Session             = Depends(get_db)
    ):
        # Busca en una sola consulta si alguno de los roles del user
        # tiene el permiso requerido
        exists = (
            db.query(models.role_permissions)
              .join(models.Permission, models.Permission.id==models.role_permissions.c.permission_id)
              .filter(
                models.role_permissions.c.role_id.in_([r.id for r in current_user.roles]),
                models.Permission.name == perm_name
              )
              .first()
        )
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para esta acción"
            )
        return current_user
    return checker