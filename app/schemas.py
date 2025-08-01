from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List, Literal
from enum import Enum


# === Enum para roles ===
class RolUsuarioEnum(str, Enum):
    administrador = "administrador"
    comprador = "comprador"


# === Autenticación ===

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    rol: Optional[RolUsuarioEnum] = None


# === Usuarios ===

class UsuarioBase(BaseModel):
    nombre_usuario: str
    nombre_completo: str
    correo: EmailStr
    telefono: Optional[str] = None


class UsuarioLogin(BaseModel):
    nombre_usuario: str
    contraseña: str


class UsuarioCompradorCreate(UsuarioBase):
    contraseña: str
    rol: RolUsuarioEnum = RolUsuarioEnum.comprador


class UsuarioAdminCreate(UsuarioBase):
    contraseña: str
    rol: RolUsuarioEnum = RolUsuarioEnum.administrador


class UsuarioResponse(UsuarioBase):
    id_usuario: int
    rol: RolUsuarioEnum
    fecha_registro: datetime

    class Config:
        orm_mode = True
        use_enum_values = True


# === Productos ===

class ProductoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    stock: int
    categoria: Optional[str] = None


class ProductoCreate(ProductoBase):
    pass


class Producto(ProductoBase):
    id_producto: int
    fecha_creacion: datetime

    class Config:
        orm_mode = True


# === Detalle de ventas ===

class DetalleVentaBase(BaseModel):
    id_producto: int
    cantidad: int
    precio_unitario: float


class DetalleVentaCreate(DetalleVentaBase):
    pass


class DetalleVenta(DetalleVentaBase):
    id_detalle: int
    subtotal: float

    class Config:
        orm_mode = True


# === Ventas ===

class VentaBase(BaseModel):
    pass


class VentaCreate(VentaBase):
    detalles: List[DetalleVentaCreate]


class Venta(VentaBase):
    id_venta: int
    id_usuario: int
    fecha_venta: datetime
    total: float
    detalles: List[DetalleVenta]

    class Config:
        orm_mode = True
