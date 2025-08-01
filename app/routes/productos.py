from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import schemas, models, dependencies
from ..database import get_db

router = APIRouter(
    prefix="/productos",
    tags=["productos"]
)


@router.get("/", response_model=List[schemas.Producto])
def leer_productos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(
        dependencies.es_administrador_o_comprador)
):
    productos = db.query(models.Producto).offset(skip).limit(limit).all()
    return productos


@router.post("/", response_model=schemas.Producto)
def crear_producto(
    producto: schemas.ProductoCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(
        dependencies.es_administrador)
):
    db_producto = models.Producto(**producto.dict())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto


@router.get("/{producto_id}", response_model=schemas.Producto)
def leer_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(
        dependencies.es_administrador_o_comprador)
):
    db_producto = db.query(models.Producto).filter(
        models.Producto.id_producto == producto_id).first()
    if db_producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return db_producto


@router.put("/{producto_id}", response_model=schemas.Producto)
def actualizar_producto(
    producto_id: int,
    producto: schemas.ProductoCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(
        dependencies.es_administrador)
):
    db_producto = db.query(models.Producto).filter(
        models.Producto.id_producto == producto_id).first()
    if db_producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    for key, value in producto.dict().items():
        setattr(db_producto, key, value)

    db.commit()
    db.refresh(db_producto)
    return db_producto


@router.delete("/{producto_id}")
def eliminar_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(
        dependencies.es_administrador)
):
    db_producto = db.query(models.Producto).filter(
        models.Producto.id_producto == producto_id).first()
    if db_producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    db.delete(db_producto)
    db.commit()
    return {"mensaje": "Producto eliminado correctamente"}
