# crud.py
from sqlalchemy.orm import Session
from app import models, schemas
from passlib.context import CryptContext
from app.crudFolder.informacion import (
    get_informacion,
    get_informaciones,
    create_informacion,
    update_informacion,
    delete_informacion,
    update_estado_informacion,
    get_totales_por_estado
)
from app.crudFolder.items import (
    get_item,
    get_items_by_informacion,
    create_item,
    update_item,
    delete_item,
    get_item_by_informacion_and_id,
)
from app.crudFolder.pagos import (
    get_pago,
    get_pagos,
    create_pago,
    update_pago,
    delete_pago,
)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed)
    if user.roles:
        roles = db.query(models.Role).filter(models.Role.id.in_(user.roles)).all()
        db_user.roles = roles
    db.add(db_user); db.commit(); db.refresh(db_user)
    return db_user

# Similar: get_role, create_role, etc.
def get_roles(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Role)
          .order_by(models.Role.id)
          .offset(skip)
          .limit(limit)
          .all()
    )

def create_role(db: Session, role_in: schemas.RoleBase):
    # Instancia el modelo
    db_role = models.Role(
        name=role_in.name,
        description=role_in.description
    )
    # Inserta en la sesión y guarda
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role
def create_permission(db: Session, name: str):
    perm = models.Permission(name=name)
    db.add(perm); db.commit(); db.refresh(perm)
    return perm

def assign_permission_to_role(db: Session, role_id: int, perm_id: int):
    role = db.get(models.Role, role_id)
    perm = db.get(models.Permission, perm_id)
    if perm not in role.permissions:
        role.permissions.append(perm)
        db.commit(); db.refresh(role)
    return role

# Listar productos (GET /products/)
def get_products(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Product)
          .order_by(models.Product.id)   # ← aquí fijas el orden
          .offset(skip)
          .limit(limit)
          .all()
    )

# Crear producto (POST /products/)
def create_product(db: Session, product_in: schemas.ProductCreate):
    db_prod = models.Product(**product_in.dict())
    db.add(db_prod)
    db.commit()
    db.refresh(db_prod)
    return db_prod

# Obtener un único producto
def get_product(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Product)
          .order_by(models.Product.id)      # ← Indica siempre un ORDER BY
          .offset(skip)
          .limit(limit)
          .all()
    )

# Actualizar producto (PUT /products/{id})
def update_product(db: Session, product_id: int, product_in: schemas.ProductCreate):
    prod = get_product(db, product_id)
    if not prod:
        return None
    for field, value in product_in.dict().items():
        setattr(prod, field, value)
    db.commit()
    db.refresh(prod)
    return prod

# Borrar producto (DELETE /products/{id})
def delete_product(db: Session, product_id: int):
    prod = get_product(db, product_id)
    if prod:
        db.delete(prod)
        db.commit()
    return prod

def get_user_menu_tree(db: Session, user_id: int):
    """
    Solo usa user_menu para traer los menús asignados a un usuario.
    """
    # 1) Trae todos los MenuItem ligados por user_menu
    items = (
        db.query(models.MenuItem)
          .join(models.user_menu, models.MenuItem.id == models.user_menu.c.menu_item_id)
          .filter(models.user_menu.c.user_id == user_id)
          .order_by(models.MenuItem.sort_order)
          .all()
    )

    # 2) Map de id → nodo
    lookup = {
        mi.id: {
            "id": mi.id,
            "name": mi.name,
            "path": mi.path,
            "icon": mi.icon,
            "parent_id": mi.parent_id,
            "sort_order" : mi.sort_order,
            "children": []
        }
        for mi in items
    }

    # 3) Ensambla el árbol
    tree = []
    for node in lookup.values():
        pid = node["parent_id"]
        if pid and pid in lookup:
            lookup[pid]["children"].append(node)
        else:
            tree.append(node)

    return tree