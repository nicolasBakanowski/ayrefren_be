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
├── requirements.txt       # Dependencias de producción
├── requirements.dev.txt   # Extras para desarrollo y pruebas
└── README.md
```

## Ejecutar con Docker

Antes de iniciar crea tu archivo de entorno:

```bash
cp .env.example .env
# edita los valores necesarios. Asegúrate de que
# `DATABASE_URL` apunte al host `db`, que es el nombre del
# contenedor de Postgres utilizado en Docker.
```

### Modo desarrollo

Levanta los servicios con recarga automática usando:

```bash
docker compose -f docker-compose.dev.yml up --build
```

Este modo monta el código como volumen y ejecuta la API con `--reload`.
Al iniciar el contenedor se ejecuta `scripts/dev_seed.py` si la variable
de entorno `DEV_SEED` vale `1`, cargando datos de ejemplo en todas las
tablas para poder probar cualquier endpoint.

### Modo producción

Para un despliegue en producción ejecuta:

```bash
docker compose -f docker-compose.prod.yml up --build
```

El contenedor espera a que la base de datos esté disponible, aplica las
migraciones, corre `init_db.py` (solo la primera vez) y finalmente inicia la
API.

Para generar nuevas migraciones manualmente puedes usar el contenedor de desarrollo:

```bash
docker compose -f docker-compose.dev.yml run --rm web alembic revision --autogenerate -m "mensaje"
```

## Pruebas automatizadas

La carpeta `tests/` contiene una suite de tests basada en `pytest` que usa
`TestClient` para levantar la aplicación con una base de datos SQLite en
memoria. Esto permite verificar cada router de forma aislada.

Para ejecutarla instale las dependencias y luego corra `pytest`:

```bash
pip install -r requirements.dev.txt
pytest -q
```

Si prefieres ejecutar las pruebas dentro de un contenedor (sin instalar nada
localmente) puedes usar el servicio de desarrollo:

```bash
docker compose -f docker-compose.dev.yml run --rm web pytest -q
```

Para obtener un reporte de cobertura:

```bash
docker compose -f docker-compose.dev.yml run --rm web \
  pytest --cov=app --cov-report=html
```

## Calcular total de una orden

La API expone el endpoint `GET /orders/{id}/total` que suma el costo de las tareas registradas y los repuestos utilizados (aplicando el incremento porcentual de cada pieza). Esto permite conocer el monto a facturar por una reparación antes de emitir la factura.

## Listar nombres de repuestos

Para poblar un selector con los repuestos que se han cargado en distintas órdenes se puede usar `GET /work-orders/parts/names`. Este endpoint devuelve una lista sin duplicados. Opcionalmente se puede filtrar por una orden específica pasando `work_order_id` como parámetro de consulta.

## Detalle de facturas con recargo

Cuando un tipo de factura define un recargo porcentual, el endpoint `GET /invoices/{id}/detail` devuelve el total original junto con el total con dicho recargo aplicado. Así el frontend puede mostrar ambos valores y elegir cuál cobrar.

## Formato de respuestas

Todos los endpoints de creación, edición y borrado responden con un HTTP 200.
El cuerpo sigue el esquema:

```json
{
  "code": 0,
  "success": true,
  "message": "opcional",
  "data": {"...": "..."}
}
```

En caso de error, `success` es `false` y `code` contiene el código
correspondiente (por ejemplo 404 cuando un recurso no existe).

## Uso de la documentación interactiva

El esquema OAuth2 está configurado con el endpoint `POST /auth/token`.  En la
parte superior de Swagger UI presioná **Authorize**, ingresá tus credenciales y
obtené automáticamente el `access_token` para las siguientes peticiones.

Si preferís hacerlo manualmente podés llamar a `POST /auth/login`, copiar el
valor del campo `access_token` de la respuesta y proporcionarlo en el diálogo de
autorización como `Bearer <token>`.  De lo contrario la documentación enviará
el header `Authorization: Bearer undefined` y verás un `401 Token inválido`.
