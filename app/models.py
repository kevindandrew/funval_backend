from sqlalchemy import (
    Column, Integer, String, Float, ForeignKey, DateTime, Enum, CheckConstraint, Text
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class RolUsuario(enum.Enum):
    administrador = "administrador"
    comprador = "comprador"


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre_usuario = Column(String(50), unique=True,
                            index=True, nullable=False)
    contraseña = Column(String, nullable=False)
    rol = Column(Enum(RolUsuario), nullable=False)
    nombre_completo = Column(String(100), nullable=False)
    telefono = Column(String(20), nullable=True)
    correo = Column(String(100), unique=True, nullable=False)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())

    ventas = relationship("Venta", back_populates="usuario")


class Producto(Base):
    __tablename__ = "productos"

    id_producto = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, index=True)
    descripcion = Column(Text)
    precio = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    categoria = Column(String(50))
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    detalles_venta = relationship("DetalleVenta", back_populates="producto")


class Venta(Base):
    __tablename__ = "ventas"

    id_venta = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey(
        "usuarios.id_usuario", ondelete="RESTRICT"), nullable=False)
    fecha_venta = Column(DateTime(timezone=True), server_default=func.now())
    total = Column(Float, nullable=False)

    usuario = relationship("Usuario", back_populates="ventas")
    detalles = relationship(
        "DetalleVenta", back_populates="venta", cascade="all, delete")


class DetalleVenta(Base):
    __tablename__ = "detalle_ventas"

    id_detalle = Column(Integer, primary_key=True, index=True)
    id_venta = Column(Integer, ForeignKey(
        "ventas.id_venta", ondelete="CASCADE"), nullable=False)
    id_producto = Column(Integer, ForeignKey(
        "productos.id_producto", ondelete="RESTRICT"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)

    venta = relationship("Venta", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles_venta")

    @property
    def subtotal(self):
        return round(self.cantidad * self.precio_unitario, 2)
