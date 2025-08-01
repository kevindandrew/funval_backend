from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv

from . import schemas, models
from .database import get_db
from passlib.context import CryptContext

# Cargar variables de entorno
load_dotenv()

# === Configuración del token ===
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# === Seguridad ===
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = HTTPBearer()  # Cambiado para usar Bearer token puro


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña coincide con el hash almacenado"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Genera un hash seguro de la contraseña"""
    return pwd_context.hash(password)


def authenticate_user(db: Session, username: str, password: str) -> Optional[models.Usuario]:
    """Autentica un usuario con nombre de usuario y contraseña"""
    user = db.query(models.Usuario).filter(
        models.Usuario.nombre_usuario == username).first()
    if not user:
        return None
    if not verify_password(password, user.contraseña):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token JWT de acceso"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    # Asegura que "rol" se serialice correctamente
    if "rol" in to_encode and hasattr(to_encode["rol"], "value"):
        to_encode["rol"] = to_encode["rol"].value

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.Usuario:
    """Obtiene el usuario actual a partir del token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials  # Extraer token del header Bearer
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = db.query(models.Usuario).filter(
        models.Usuario.nombre_usuario == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: models.Usuario = Depends(get_current_user)
) -> models.Usuario:
    """Verifica que el usuario esté activo"""
    if not current_user:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user


def es_administrador(
    current_user: models.Usuario = Depends(get_current_active_user)
) -> models.Usuario:
    """Verifica que el usuario sea administrador"""
    if current_user.rol != models.RolUsuario.administrador:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción"
        )
    return current_user


def es_administrador_o_comprador(
    current_user: models.Usuario = Depends(get_current_active_user)
) -> models.Usuario:
    """Verifica que el usuario sea administrador o comprador"""
    if current_user.rol not in [models.RolUsuario.administrador, models.RolUsuario.comprador]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción"
        )
    return current_user
