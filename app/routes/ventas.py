from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app import schemas, models, dependencies
from ..database import get_db

router = APIRouter(
    prefix="/ventas",
    tags=["ventas"]
)


@router.post("/", response_model=schemas.Venta)
def crear_venta(
    venta: schemas.VentaCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(
        dependencies.es_administrador_o_comprador)
):
    detalles_db = []
    total = 0.0

    # Validación y armado de detalles
    for detalle in venta.detalles:
        producto = db.query(models.Producto).filter(
            models.Producto.id_producto == detalle.id_producto).first()
        if not producto:
            raise HTTPException(
                status_code=404, detail=f"Producto con ID {detalle.id_producto} no encontrado")
        if producto.stock < detalle.cantidad:
            raise HTTPException(
                status_code=400, detail=f"Stock insuficiente para el producto {producto.nombre}")

        subtotal = detalle.cantidad * detalle.precio_unitario
        total += subtotal

        detalles_db.append(models.DetalleVenta(
            id_producto=detalle.id_producto,
            cantidad=detalle.cantidad,
            precio_unitario=detalle.precio_unitario
        ))

    # Crear la venta
    db_venta = models.Venta(
        id_usuario=current_user.id_usuario,
        total=total,
        detalles=detalles_db
    )

    # Descontar stock
    for detalle in venta.detalles:
        producto = db.query(models.Producto).filter(
            models.Producto.id_producto == detalle.id_producto).first()
        producto.stock -= detalle.cantidad

    db.add(db_venta)
    db.commit()
    db.refresh(db_venta)
    return db_venta


@router.get("/", response_model=List[schemas.Venta])
def leer_ventas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(dependencies.es_administrador)
):
    """Solo administradores pueden ver todas las ventas"""
    ventas = db.query(models.Venta).offset(skip).limit(limit).all()
    return ventas


@router.get("/mis-ventas", response_model=List[schemas.Venta])
def leer_mis_ventas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(
        dependencies.es_administrador_o_comprador)
):
    """Los compradores pueden ver solo sus propias ventas, administradores ven todas"""
    if current_user.rol == models.RolUsuario.administrador:
        ventas = db.query(models.Venta).offset(skip).limit(limit).all()
    else:
        ventas = db.query(models.Venta).filter(
            models.Venta.id_usuario == current_user.id_usuario).offset(skip).limit(limit).all()
    return ventas


@router.get("/{venta_id}", response_model=schemas.Venta)
def leer_venta(
    venta_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(
        dependencies.es_administrador_o_comprador)
):
    venta = db.query(models.Venta).filter(
        models.Venta.id_venta == venta_id).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")

    if current_user.rol != models.RolUsuario.administrador and venta.id_usuario != current_user.id_usuario:
        raise HTTPException(
            status_code=403, detail="No tienes permiso para ver esta venta")

    return venta
