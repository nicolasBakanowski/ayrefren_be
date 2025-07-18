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

Para levantar la aplicación y aplicar las migraciones automáticamente:

```bash
docker compose up --build
```

El servicio `migrate` ejecuta `alembic upgrade head` y, una vez finalizado,
inicia el servicio `web`.


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


