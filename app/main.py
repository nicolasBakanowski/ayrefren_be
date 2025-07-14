from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    auth_router,
    clients_router,
    invoice_router,
    parts_router,
    reports_router,
    trucks_router,
    users_router,
    work_order_parts_router,
    work_order_tasks_router,
    work_orders_mechanic_router,
    work_orders_router,
)


# Configuración de la app
def get_application() -> FastAPI:
    app = FastAPI(
        title="Sistema de Gestión para Taller Mecánico",
        description="API para gestionar órdenes de trabajo, clientes, facturación, pagos y más.",
        version="1.0.0",
        docs_url="/docs",
    )

    # Middleware CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Podés restringir esto en producción
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Incluir routers
    include_routers(app)

    return app


# Inclusión modular de rutas
def include_routers(app: FastAPI) -> None:
    app.include_router(auth_router, prefix="/auth", tags=["Autenticación"])

    app.include_router(clients_router, prefix="/clients", tags=["Clientes"])
    app.include_router(users_router, prefix="/users", tags=["Usuarios"])
    app.include_router(
        work_orders_router, prefix="/orders", tags=["Órdenes de Trabajo"]
    )
    app.include_router(
        work_orders_mechanic_router,
        prefix="/work-orders/mechanics",
        tags=["Mecánicos en Órdenes"],
    )
    app.include_router(
        work_order_tasks_router, prefix="/work-orders/tasks", tags=["Tareas de Órdenes"]
    )

    app.include_router(
        work_order_parts_router,
        prefix="/work-orders/parts",
        tags=["Repuestos en Órdenes"],
    )
    app.include_router(invoice_router, prefix="/invoices", tags=["Facturación"])

    app.include_router(reports_router, prefix="/reports", tags=["Reportes"])

    app.include_router(trucks_router, prefix="/trucks", tags=["Camiones"])

    app.include_router(parts_router, prefix="/parts", tags=["Repuestos"])


# Inicializa la app
app = get_application()
