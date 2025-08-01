# API Supermercado

API para gestión de supermercado con autenticación por roles desarrollada con FastAPI.

## Características

- Autenticación JWT con roles (administrador y comprador)
- Gestión de productos
- Gestión de usuarios
- Gestión de ventas
- Base de datos PostgreSQL

## Instalación

1. Clona el repositorio:

```bash
git clone <url-del-repositorio>
cd <nombre-del-proyecto>
```

2. Crea un entorno virtual:

```bash
python -m venv .venv
```

3. Activa el entorno virtual:

```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

4. Instala las dependencias:

```bash
pip install -r requirements.txt
```

5. Configura las variables de entorno:

```bash
# Copia el archivo de ejemplo
cp .env.example .env

# Edita el archivo .env con tus configuraciones
```

6. Configura tu base de datos PostgreSQL y actualiza la variable `DATABASE_URL` en el archivo `.env`

7. Ejecuta la aplicación:

```bash
uvicorn app.main:app --reload
```

## Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/nombre_base_datos
SECRET_KEY=tu_clave_secreta_muy_larga_y_compleja
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Documentación de la API

Una vez que la aplicación esté ejecutándose, puedes acceder a:

- Documentación Swagger: `http://localhost:8000/docs`
- Documentación ReDoc: `http://localhost:8000/redoc`
- Información de permisos: `http://localhost:8000/permisos`

## Estructura del Proyecto

```
app/
├── __init__.py
├── main.py              # Aplicación principal FastAPI
├── database.py          # Configuración de la base de datos
├── dependencies.py      # Dependencias de autenticación
├── models.py            # Modelos SQLAlchemy
├── schemas.py           # Esquemas Pydantic
└── routes/              # Rutas de la API
    ├── __init__.py
    ├── auth.py          # Autenticación
    ├── productos.py     # Gestión de productos
    ├── usuarios.py      # Gestión de usuarios
    └── ventas.py        # Gestión de ventas
```

## Roles y Permisos

### Endpoints Públicos:

- `POST /login` - Iniciar sesión
- `POST /registro-comprador` - Registro de compradores

### Solo Administrador:

- `POST /registro-admin` - Crear administradores
- `POST /productos` - Crear productos
- `PUT /productos/{id}` - Actualizar productos
- `DELETE /productos/{id}` - Eliminar productos
- `GET /ventas` - Ver todas las ventas
- `GET /usuarios` - Ver todos los usuarios
- `GET /usuarios/{id}` - Ver usuario específico
- `PUT /usuarios/{id}` - Actualizar usuario
- `DELETE /usuarios/{id}` - Eliminar usuario

### Administrador y Comprador:

- `GET /productos` - Ver productos
- `GET /productos/{id}` - Ver producto específico
- `POST /ventas` - Crear ventas
- `GET /ventas/{id}` - Ver venta específica
- `GET /ventas/mis-ventas` - Ver mis propias ventas
- `GET /usuarios/me/perfil` - Ver mi perfil
- `PUT /usuarios/me/perfil` - Actualizar mi perfil

## Tecnologías Utilizadas

- **FastAPI** - Framework web
- **SQLAlchemy** - ORM
- **PostgreSQL** - Base de datos
- **JWT** - Autenticación
- **Bcrypt** - Encriptación de contraseñas
- **Pydantic** - Validación de datos
