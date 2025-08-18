# main.py
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import schemas
from app.routers import pagos, products, users, roles, informacion, items
from app.auth import get_db, authenticate_user, create_access_token
from datetime import timedelta
import app.config as config
from fastapi.middleware.cors import CORSMiddleware    # <— importa aquí
import app.crud as crud


app = FastAPI(
  docs_url="/docs",
  redoc_url="/redoc",
  openapi_url="/openapi.json"
)
# ——— Habilitar CORS justo después de crear 'app' —————
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://172.16.10.38:4200"],  # o tu URL de Angular
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)
# Login
# @app.post("/token", response_model=schemas.Token)
# def login(
#     form_data: OAuth2PasswordRequestForm = Depends(),
#     db: Session = Depends(get_db)
# ):
#     user = authenticate_user(db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Credenciales inválidas",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token = create_access_token(
#         data={"sub": user.username, "roles": [r.name for r in user.roles]},
#         expires_delta=timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES),
#     )
#     menus = crud.get_user_menu_tree(db, user.id)
#     return {"access_token": access_token, "token_type": "bearer","menus": menus}
@app.post("/token", response_model=schemas.LoginResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # 1) Autenticar usuario
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2) Generar JWT
    access_token = create_access_token(
        data={"sub": user.username, "roles": [r.name for r in user.roles]},
        expires_delta=timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    # 3) Recuperar solo menús asignados vía user_menu
    menus = crud.get_user_menu_tree(db, user.id)

    # 4) Devolver token + menús
    return {
        "access_token": access_token,
        "token_type":   "bearer",
        "menus":        menus
    }
# Incluir routers
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(products.router) 
app.include_router(informacion.router)
app.include_router(items.router)
app.include_router(pagos.router)
#uvicorn app.main:app --reload
#uvicorn app.main:app --host 172.16.10.38 --port 5050 --reload
#uvicorn app.main:app --host 192.168.18.12 --port 5050 --reload

#172.16.10.37

