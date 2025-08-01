from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from sqlalchemy.orm import Session

from .. import schemas, models, dependencies
from ..database import get_db

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=schemas.Token)
async def login_for_access_token(
    form_data: schemas.UsuarioLogin,
    db: Session = Depends(get_db)
):
    user = dependencies.authenticate_user(
        db, form_data.nombre_usuario, form_data.contraseña)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=dependencies.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = dependencies.create_access_token(
        data={"sub": user.nombre_usuario, "rol": user.rol},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/registro-comprador", response_model=schemas.UsuarioResponse)
def registrar_comprador(
    usuario: schemas.UsuarioCompradorCreate,
    db: Session = Depends(get_db)
):
    # Verificar si el usuario ya existe
    db_user = db.query(models.Usuario).filter(
        models.Usuario.nombre_usuario == usuario.nombre_usuario).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Nombre de usuario ya registrado"
        )

    # Verificar si el correo ya está registrado
    db_email = db.query(models.Usuario).filter(
        models.Usuario.correo == usuario.correo).first()
    if db_email:
        raise HTTPException(
            status_code=400,
            detail="Correo electrónico ya registrado"
        )

    # Crear usuario con rol de comprador
    hashed_password = dependencies.get_password_hash(usuario.contraseña)
    db_usuario = models.Usuario(
        nombre_usuario=usuario.nombre_usuario,
        contraseña=hashed_password,
        rol=models.RolUsuario.comprador,  # Usar el enum
        nombre_completo=usuario.nombre_completo,
        telefono=usuario.telefono,
        correo=usuario.correo
    )

    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


@router.post("/registro-admin", response_model=schemas.UsuarioResponse)
def registrar_administrador(
    usuario: schemas.UsuarioAdminCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(dependencies.es_administrador)
):
    # Verificar si el usuario ya existe
    db_user = db.query(models.Usuario).filter(
        models.Usuario.nombre_usuario == usuario.nombre_usuario).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Nombre de usuario ya registrado"
        )

    # Verificar si el correo ya está registrado
    db_email = db.query(models.Usuario).filter(
        models.Usuario.correo == usuario.correo).first()
    if db_email:
        raise HTTPException(
            status_code=400,
            detail="Correo electrónico ya registrado"
        )

    # Crear usuario administrador
    hashed_password = dependencies.get_password_hash(usuario.contraseña)
    db_usuario = models.Usuario(
        nombre_usuario=usuario.nombre_usuario,
        contraseña=hashed_password,
        rol=models.RolUsuario.administrador,  # Usar el enum
        nombre_completo=usuario.nombre_completo,
        telefono=usuario.telefono,
        correo=usuario.correo
    )

    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario
