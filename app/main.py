# main.py
from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from app import schemas
from app.routers import pagos, products, users, roles, informacion, items, detalle_proceso,extractor
from app.auth import get_db, authenticate_user, create_access_token
from datetime import timedelta
import app.config as config
from fastapi.middleware.cors import CORSMiddleware  # <— importa aquí
import app.crud as crud
import logging



logger = logging.getLogger("uvicorn.error")

app = FastAPI(docs_url="/docs", redoc_url="/redoc", openapi_url="/openapi.json")
# ——— Habilitar CORS justo después de crear 'app' —————
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # o tu URL de Angular
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Errores que lanza con HTTPException
    payload = {
        "detail": exc.detail if exc.detail else "Error HTTP",
        "code": exc.status_code,
        "path": str(request.url.path),
    }
    return JSONResponse(status_code=exc.status_code, content=payload)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Cualquier error no controlado
    logger.exception("Unhandled error")
    payload = {
        "detail": "Error interno del servidor",
        "code": 500,
        "path": str(request.url.path),
        # opcional en dev: "trace": traceback.format_exc()
    }
    return JSONResponse(status_code=500, content=payload)


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
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
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
    return {"access_token": access_token, "token_type": "bearer", "menus": menus}


# Incluir routers
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(products.router)
app.include_router(informacion.router)
app.include_router(items.router)
app.include_router(pagos.router)
app.include_router(detalle_proceso.router)
app.include_router(extractor.router)

# uvicorn app.main:app --reload
# uvicorn app.main:app --host 172.16.10.36 --port 5050 --reload
# uvicorn app.main:app --host 192.168.18.12 --port 5050 --reload

# 172.16.10.37
