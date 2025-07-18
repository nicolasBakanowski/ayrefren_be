```
ayre_fren_ba/
├── app/
│   ├── core/             # Configuraciones globales (DB, auth, etc.)
│   ├── models/           # Modelos Pydantic y SQLAlchemy
│   ├── routers/          # Rutas organizadas por módulo (clientes, pagos, etc.)
│   ├── services/         # Lógica de negocio
│   ├── schemas/          # Pydantic para inputs/outputs
│   ├── deps/             # Dependencias reutilizables
│   └── main.py           # App FastAPI
├── alembic/              # Migraciones de base de datos
├── .env                  # Variables de entorno
├── requirements.txt
└── README.md
```

## Ejecutar con Docker

Antes de iniciar crea tu archivo de entorno:

```bash
cp .env.example .env
# edita los valores necesarios
```

### Modo desarrollo

Levanta los servicios con recarga automática usando:

```bash
docker compose -f docker-compose.dev.yml up --build
```

Este modo monta el código como volumen y ejecuta la API con `--reload`.

### Modo producción

Para un despliegue en producción ejecuta:

```bash
docker compose -f docker-compose.prod.yml up --build
```

El contenedor espera a que la base de datos esté disponible, aplica las
migraciones, corre `init_db.py` (solo la primera vez) y finalmente inicia la
API.

Para generar nuevas migraciones manualmente:

```bash
alembic revision --autogenerate -m "mensaje"
```

## Pruebas automatizadas

La carpeta `tests/` contiene una suite de tests basada en `pytest` que usa
`TestClient` para levantar la aplicación con una base de datos SQLite en
memoria. Esto permite verificar cada router de forma aislada.

Para ejecutarla instale las dependencias y luego corra `pytest`:

```bash
pip install -r requirements.txt
pytest -q
```

## Validación de claves foráneas

Todos los servicios emplean la función `validate_foreign_keys` ubicada en
`app/core/validators.py` para asegurar que los identificadores referenciados
existen antes de crear o actualizar datos. Si alguna clave no es válida, el
endpoint responde con un `404` en lugar de un error 500.


