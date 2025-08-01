from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, productos, usuarios, ventas
from app.database import engine, Base


#    !!!!!!!! ATENCION NO TOCAR, FUNCIONA Y NO SE PORQUE !!!!!!!!!!

#    ESTE FRAGMENTO DE CODIGO FUE ESCRITO ENTRE LAS 2 Y 3 DE LA MAÑANA
#    BAJO LOS EFECTOS COMBINADOS DE LA CAFEINA, DESESPERACION Y UN BUG Q SOLO
#    SE MANIFIESTA CUANDO NADIE LO ESTA MIRANDO.

#    No funciona si lo entiendes
#    No lo entiendes si funciona

#    cualquier intento de refactorizar esto ha
#    resultado en la invocacion de problemas dimensionales, loops infinitos
#    y un extraño parpadeo en el monitor que aun no puedo explicar.

#    si necesitas cambiar esto, primero haz una oracion, luego haz una copia de seguridad,
#    y por ultimo suerte.


# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Supermercado",
    description="API para gestión de supermercado con autenticación por roles",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas las origenes
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos HTTP
    allow_headers=["*"],  # Permite todos los headers
)

# Incluir los routers
app.include_router(auth.router)
app.include_router(productos.router)
app.include_router(usuarios.router)
app.include_router(ventas.router)


@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API del Supermercado"}


@app.get("/permisos")
def info_permisos():
    return {
        "endpoints_publicos": [
            "POST /login - Iniciar sesión",
            "POST /registro-comprador - Registro de compradores"
        ],
        "endpoints_solo_administrador": [
            "POST /registro-admin - Crear administradores",
            "POST /productos - Crear productos",
            "PUT /productos/{id} - Actualizar productos",
            "DELETE /productos/{id} - Eliminar productos",
            "GET /ventas - Ver todas las ventas",
            "GET /usuarios - Ver todos los usuarios",
            "GET /usuarios/{id} - Ver usuario específico",
            "PUT /usuarios/{id} - Actualizar usuario",
            "DELETE /usuarios/{id} - Eliminar usuario"
        ],
        "endpoints_administrador_y_comprador": [
            "GET /productos - Ver productos",
            "GET /productos/{id} - Ver producto específico",
            "POST /ventas - Crear ventas",
            "GET /ventas/{id} - Ver venta específica",
            "GET /ventas/mis-ventas - Ver mis propias ventas",
            "GET /usuarios/me/perfil - Ver mi perfil",
            "PUT /usuarios/me/perfil - Actualizar mi perfil"
        ]
    }
