from .auth import auth_router
from .clients import clients_router
from .expenses import expenses_router
from .invoices import invoice_router
from .reports import reports_router
from .trucks import trucks_router
from .users import users_router
from .work_order_parts import work_order_parts_router
from .work_order_tasks import work_order_tasks_router
from .work_orders import work_orders_router
from .work_orders_mechanic import work_orders_mechanic_router
from .work_orders_reviewer import work_orders_reviewer_router

__all__ = [
    "clients_router",
    "users_router",
    "work_orders_router",
    "work_orders_mechanic_router",
    "work_order_tasks_router",
    "work_order_parts_router",
    "invoice_router",
    "reports_router",
    "trucks_router",
    "auth_router",
    "expenses_router",
    "work_orders_reviewer_router",
]
