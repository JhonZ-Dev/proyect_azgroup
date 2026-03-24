# schemas.py
from pydantic import BaseModel
from typing import List, Optional

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class Role(RoleBase):
    id: int
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    job_title: Optional[str] = None
    ruc: Optional[str] = None

class UserCreate(UserBase):
    password: str
    roles: List[int] = []

class UserRead(UserBase):
    id: int
    is_active: bool
    roles: List[Role] = []
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
# 1) Define la base (lo que tienen en común create y read)
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

# 2) Schema para creación (puede heredar todo lo de ProductBase)
class ProductCreate(ProductBase):
    pass

# 3) Schema para lectura (añade el id y habilita from_attributes)
class ProductRead(ProductBase):
    id: int

    class Config:
        from_attributes = True


class MenuItem(BaseModel):
    id: int
    name: str
    path: Optional[str] = None
    icon: Optional[str] = None
    sort_order: int   
    children: List["MenuItem"] = []  # recursivo

    class Config:
        from_attributes = True

MenuItem.update_forward_refs()

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    menus: List[MenuItem]