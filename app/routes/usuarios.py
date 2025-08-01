from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import schemas, models, dependencies
from ..database import get_db

router = APIRouter(
    prefix="/usuarios",
    tags=["usuarios"]
)


@router.get("/", response_model=List[schemas.UsuarioResponse])
def leer_usuarios(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(dependencies.es_administrador)
):
    """Solo administradores pueden ver la lista de usuarios"""
    usuarios = db.query(models.Usuario).offset(skip).limit(limit).all()
    return usuarios


@router.get("/{usuario_id}", response_model=schemas.UsuarioResponse)
def leer_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(dependencies.es_administrador)
):
    """Solo administradores pueden ver información de otros usuarios"""
    db_usuario = db.query(models.Usuario).filter(
        models.Usuario.id_usuario == usuario_id).first()
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_usuario


@router.put("/{usuario_id}", response_model=schemas.UsuarioResponse)
def actualizar_usuario(
    usuario_id: int,
    usuario_data: schemas.UsuarioBase,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(dependencies.es_administrador)
):
    """Solo administradores pueden actualizar información de usuarios"""
    db_usuario = db.query(models.Usuario).filter(
        models.Usuario.id_usuario == usuario_id).first()
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Actualizar solo los campos permitidos (no contraseña ni rol)
    db_usuario.nombre_completo = usuario_data.nombre_completo
    db_usuario.telefono = usuario_data.telefono
    db_usuario.correo = usuario_data.correo

    db.commit()
    db.refresh(db_usuario)
    return db_usuario


@router.delete("/{usuario_id}")
def eliminar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(dependencies.es_administrador)
):
    """Solo administradores pueden eliminar usuarios"""
    if usuario_id == current_user.id_usuario:
        raise HTTPException(
            status_code=400,
            detail="No puedes eliminar tu propia cuenta"
        )

    db_usuario = db.query(models.Usuario).filter(
        models.Usuario.id_usuario == usuario_id).first()
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db.delete(db_usuario)
    db.commit()
    return {"mensaje": "Usuario eliminado correctamente"}


@router.get("/me/perfil", response_model=schemas.UsuarioResponse)
def leer_perfil_propio(
    current_user: models.Usuario = Depends(
        dependencies.get_current_active_user)
):
    """Cualquier usuario autenticado puede ver su propio perfil"""
    return current_user


@router.put("/me/perfil", response_model=schemas.UsuarioResponse)
def actualizar_perfil_propio(
    usuario_data: schemas.UsuarioBase,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(
        dependencies.get_current_active_user)
):
    """Cualquier usuario autenticado puede actualizar su propio perfil"""
    # Verificar si el nuevo correo ya está en uso por otro usuario
    if usuario_data.correo != current_user.correo:
        db_email = db.query(models.Usuario).filter(
            models.Usuario.correo == usuario_data.correo,
            models.Usuario.id_usuario != current_user.id_usuario
        ).first()
        if db_email:
            raise HTTPException(
                status_code=400,
                detail="Correo electrónico ya registrado por otro usuario"
            )

    # Actualizar perfil
    current_user.nombre_completo = usuario_data.nombre_completo
    current_user.telefono = usuario_data.telefono
    current_user.correo = usuario_data.correo

    db.commit()
    db.refresh(current_user)
    return current_user
