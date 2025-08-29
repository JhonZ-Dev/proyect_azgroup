# models.py
from sqlalchemy import Column, Float, Integer, String, Boolean, DateTime, Table, ForeignKey,Date, Time, func
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

# ——— Tablas intermedias ————————————————————————————————————
user_roles = Table(
    'user_roles', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
)

role_permissions = Table(
    'role_permissions', Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True),
)

role_menu = Table(
    'role_menu', Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('menu_item_id', Integer, ForeignKey('menu_items.id'), primary_key=True),
)
user_menu = Table(
    'user_menu', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('menu_item_id', Integer, ForeignKey('menu_items.id'), primary_key=True),
)
# ——— Modelos —————————————————————————————————————————————

class User(Base):
    __tablename__ = 'users'

    id              = Column(Integer, primary_key=True, index=True)
    username        = Column(String(50), unique=True, index=True, nullable=False)
    email           = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime, default=datetime.utcnow)

    # Roles asignados
    roles = relationship(
        'Role', secondary=user_roles, back_populates='users'
    )

    # Overrides puntuales de menú
    menu_overrides = relationship(
        'UserMenuOverride', back_populates='user', cascade='all, delete-orphan'
    )
    menu_items = relationship(
        'MenuItem',
        secondary=user_menu,
        back_populates='users'
    )


class Role(Base):
    __tablename__ = 'roles'

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)

    # Usuarios que tienen este rol
    users = relationship(
        'User', secondary=user_roles, back_populates='roles'
    )

    # Permisos asignados
    permissions = relationship(
        'Permission', secondary=role_permissions, back_populates='roles'
    )

    # Menús a los que este rol tiene acceso
    menu_items = relationship(
        'MenuItem', secondary=role_menu, back_populates='roles'
    )


class Permission(Base):
    __tablename__ = 'permissions'

    id   = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    roles = relationship(
        'Role', secondary=role_permissions, back_populates='permissions'
    )


class Product(Base):
    __tablename__ = 'products'

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(100), nullable=False, index=True)
    description = Column(String(255), nullable=True)
    price       = Column(Float, nullable=False)


class MenuItem(Base):
    __tablename__ = 'menu_items'

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(100), nullable=False)
    path       = Column(String(255), nullable=True)
    icon       = Column(String(50), nullable=True)
    parent_id  = Column(Integer, ForeignKey('menu_items.id'), nullable=True)
    sort_order = Column(Integer, default=0)

    # Relaciones recursivas para anidación
    parent   = relationship(
        'MenuItem', remote_side=[id], back_populates='children'
    )
    children = relationship(
        'MenuItem', back_populates='parent', cascade='all, delete'
    )

    # Qué roles pueden ver este ítem
    roles = relationship(
        'Role', secondary=role_menu, back_populates='menu_items'
    )

    # Overrides puntuales de usuario
    user_overrides = relationship(
        'UserMenuOverride', back_populates='menu_item', cascade='all, delete-orphan'
    )
    users = relationship(
        'User',
        secondary=user_menu,
        back_populates='menu_items'
    )


class UserMenuOverride(Base):
    __tablename__ = 'user_menu_override'

    user_id      = Column(Integer, ForeignKey('users.id'), primary_key=True)
    menu_item_id = Column(Integer, ForeignKey('menu_items.id'), primary_key=True)
    is_allowed   = Column(Boolean, nullable=False, default=True)

    user      = relationship('User', back_populates='menu_overrides')
    menu_item = relationship('MenuItem', back_populates='user_overrides')


class Estado(Base):
    __tablename__ = "estados"

    id   = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False, unique=True)
    # Relación inversa (opcional)
    informaciones = relationship("Informacion", back_populates="estado")
     # Nueva relación inversa hacia tb_pagos
    pagos         = relationship("Pago", back_populates="estado")


class Informacion(Base):
    __tablename__ = 'tb_informacion'
    proforma_id     = Column(Integer, primary_key=True, index=True)
    txt_cliente     = Column(String(255), nullable=True)
    txt_ruc = Column(String(13), nullable=True)
    txt_direccion = Column(String(255), nullable=True)
    txt_fecha = Column(Date, nullable=True)
    txt_telefono = Column(String(11), nullable=True)
    txt_necesidad = Column(String(255), nullable=True)
    txt_funcionario = Column(String(255), nullable=True)
    txt_correo = Column(String(255), nullable=True)
    tHora_maxina = Column(String(255), nullable=True)
    txt_objetivoCompra = Column(String(255), nullable=True)
     # --- NUEVOS CAMPOS que acabas de agregar en la DB:
    txt_plazoEntrega       = Column(String(255), nullable=True)
    txt_vigenciaOferta     = Column(String(255), nullable=True)
    txt_garantia           = Column(String(255), nullable=True)
    txt_formaPago          = Column(String(255), nullable=True)
    txt_metodologiaTrabajo = Column(String(255), nullable=True)
    txt_enlace             = Column(String(255), nullable=True)
    txt_infimaNro          = Column(String(255), nullable=True)
    txtUsuarioRegistra     = Column(String(255), nullable=True)
    dFechaRegistro = Column(
        Date,
        nullable=False,
        server_default=func.getdate()   # o como lo definas en tu DB
    )
    tTimeHora      = Column(
        Time,
        nullable=False,
        server_default=func.getdate()   # si tu motor lo soporta, o usa default=lambda: datetime.utcnow().time()
    )
     # ——— NUEVA COLUMNA estado_id ——
    estado_id = Column(
        Integer,
        ForeignKey("estados.id"),
        nullable=False
    )
    estado = relationship("Estado", back_populates="informaciones")
    items = relationship("Item", back_populates="informacion", cascade="all, delete")
    @property
    def estado_name(self) -> str:
        # devuelve el name de la relación Estado
        return self.estado.name if self.estado else ""

class Item(Base):
    __tablename__ = 'tb_items'
    items_id        = Column(Integer, primary_key=True, index=True)
    txt_cpc         = Column(String(255), nullable=True)
    txt_unidad      = Column(String(255), nullable=True)
    txt_especificaciones = Column(String(255), nullable=True)
    int_cantidad = Column(Integer, nullable=True)
    flo_precioUnitario = Column(Float, nullable=True)
    flo_precioTotal = Column(Float, nullable=True)
    flo_total = Column(Float, nullable=True) 
    proforma_id     = Column(Integer, ForeignKey('tb_informacion.proforma_id'))
    informacion     = relationship("Informacion", back_populates="items")


class Pago(Base):
    __tablename__ = 'tb_pagos'
    idPagos        = Column(Integer, primary_key=True, index=True)
    txtFormaPago   = Column(String(100), nullable=True)
    txtUsuarioPaga = Column(String(100), nullable=True)
    txtUsuarioRecibe = Column(String(100), nullable=True)
    dFechaPago = Column(Date, nullable=True)
    tHoraPago = Column(Time, nullable=True)
    txtUsuarioCorreo = Column(String(100), nullable=True)
    txtMontoPagar = Column(Float, nullable=True)
    txtMongoPagarTexto = Column(String(255), nullable=True)
    dFechaRegistro = Column(Date,nullable=False,server_default=func.getdate())
    tTimeHora      = Column(Time,nullable=False,server_default=func.getdate())
    estado_id = Column(
        Integer,
        ForeignKey("estados.id"),
        nullable=False
    )
    estado = relationship("Estado", back_populates="pagos")
    @property
    def estado_name(self) -> str:
        # devuelve el name de la relación Estado
        return self.estado.name if self.estado else ""
    

class EstadoDetalle(Base):
    __tablename__ = "estado_detalle"

    estado_id = Column(Integer, primary_key=True)
    estado = Column(String(100), nullable=False, unique=True)

    # Relación "uno a muchos" hacia DetalleProceso
    detalle_procesos = relationship(
        "DetalleProceso",
        back_populates="estado",
        # opcional:
        # cascade="all, delete-orphan",
        # lazy="selectin",
    )
class DetalleProceso(Base):
    __tablename__ = 'tb_detalleprocesos'
    detalle_id        = Column(Integer, primary_key=True, index=True)
    txt_oferente      = Column(String(200), nullable=True)
    txt_proforma = Column(String(500), nullable=True)
    txt_fecha_proforma = Column(String(500), nullable=True)
    txt_codigo_proceso = Column(String(500), nullable=True)
    txt_entidad_contratante = Column(String(500), nullable=True)
    txt_objeto_compra = Column(String(500), nullable=True)
    int_valor_contrato = Column(Integer, nullable=True)
    txt_plazocontractual = Column(String(100), nullable=True)
    txt_firmacontrato = Column(String(100), nullable=True)
    txt_fechafin = Column(String(100), nullable=True)
    txt_fechaentrega = Column(String(100), nullable=True)
    int_diasmora = Column(Integer, nullable=True)
    txtUsuarioRegistra =  Column(String(100), nullable=True)
    dFechaRegistro = Column(Date,nullable=False,server_default=func.getdate())
    tTimeHora      = Column(Time,nullable=False,server_default=func.getdate())
    estado_id = Column(
        Integer,
        ForeignKey("estado_detalle.estado_id"),  # <--- tabla.columna
        nullable=False,
    )
    
    # Lado "muchos a uno" hacia EstadoDetalle
    estado = relationship(
        "EstadoDetalle",
        back_populates="detalle_procesos",
    )
    @property
    def estado_name(self) -> str:
        # devuelve el name de la relación Estado
        return self.estado.estado if self.estado else ""





 