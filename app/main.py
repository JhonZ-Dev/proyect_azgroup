# main.py
from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from app import schemas
from app.routers import pagos, products, users, roles, informacion, items, detalle_proceso, extractor,info_cotizaciones, estado_detalle
from app.auth import get_db, authenticate_user, create_access_token
from datetime import timedelta
import app.config as config
from fastapi.middleware.cors import CORSMiddleware  # <— importa aquí
import app.crud as crud
import logging
import secrets
import os
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

logger = logging.getLogger("uvicorn.error")

# ---------- App ----------
# Desactivamos docs/redoc/openapi por defecto para controlarlos manualmente
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

# ——— Habilitar CORS justo después de crear 'app' —————
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # o tu URL de Angular
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# ---------- Manejo de errores ----------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # 🔑 Si es un 401 con cabeceras (ej. WWW-Authenticate), lo dejamos pasar tal cual
    if exc.status_code == status.HTTP_401_UNAUTHORIZED and exc.headers:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers
        )

    payload = {
        "detail": exc.detail if exc.detail else "Error HTTP",
        "code": exc.status_code,
        "path": str(request.url.path),
    }
    return JSONResponse(status_code=exc.status_code, content=payload)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error")
    payload = {
        "detail": "Error interno del servidor",
        "code": 500,
        "path": str(request.url.path),
    }
    return JSONResponse(status_code=500, content=payload)

# ---------- Login ----------
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

# ---------- Routers ----------
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(products.router)
app.include_router(informacion.router)
app.include_router(items.router)
app.include_router(pagos.router)
app.include_router(detalle_proceso.router)
app.include_router(extractor.router)
app.include_router(info_cotizaciones.router)
app.include_router(estado_detalle.router)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ---------- Seguridad para /docs y /openapi ----------
security = HTTPBasic()

DOCS_USER = os.getenv("DOCS_USER", "jhon.zambrano")
DOCS_PASS = os.getenv("DOCS_PASS", "jhon.zambrano@2023")

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, DOCS_USER)
    correct_password = secrets.compare_digest(credentials.password, DOCS_PASS)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/docs", include_in_schema=False)
def custom_swagger_ui(credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Documentación protegida",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png"
    )

@app.get("/openapi.json", include_in_schema=False)
def custom_openapi(credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    return get_openapi(title="API protegida", version="1.0.0", routes=app.routes)

# uvicorn app.main:app --reload
# uvicorn app.main:app --host 172.16.10.36 --port 5050 --reload
# uvicorn app.main:app --host 192.168.18.12 --port 5050 --reload
# 172.16.10.37
