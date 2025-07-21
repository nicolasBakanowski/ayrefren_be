from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.constants.response_codes import ResponseCode
from app.routers import (
    auth_router,
    clients_router,
    invoice_router,
    expenses_router,
    parts_router,
    reports_router,
    trucks_router,
    users_router,
    work_order_parts_router,
    work_order_tasks_router,
    work_orders_mechanic_router,
    work_orders_reviewer_router,
    work_orders_router,
)
from app.schemas.response import ResponseSchema


# Configuración de la app
def get_application() -> FastAPI:
    app = FastAPI(
        title="Sistema de Gestión para Taller Mecánico",
        description="API para gestionar órdenes de trabajo, clientes, facturación, pagos y más.",
        version="1.0.0",
        docs_url="/docs",
    )

    @app.exception_handler(HTTPException)
    async def custom_http_exception_handler(request, exc: HTTPException):
        return JSONResponse(
            status_code=200,
            content=ResponseSchema(
                code=exc.status_code,
                success=False,
                message=exc.detail,
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request, exc: Exception):
        return JSONResponse(
            status_code=200,
            content=ResponseSchema(
                code=ResponseCode.INTERNAL_ERROR,
                success=False,
                message=str(exc),
            ).model_dump(),
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

    app.include_router(
        work_orders_reviewer_router,
        prefix="/work-orders/reviewer",
        tags=["Revisores de Órdenes"],
    )
    app.include_router(invoice_router, prefix="/invoices", tags=["Facturación"])

    app.include_router(reports_router, prefix="/reports", tags=["Reportes"])

    app.include_router(trucks_router, prefix="/trucks", tags=["Camiones"])

    app.include_router(expenses_router, tags=["Gastos"])
    app.include_router(parts_router, prefix="/parts", tags=["Repuestos"])


# Inicializa la app
app = get_application()
