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
