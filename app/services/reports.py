from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class ReportsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def profit_by_order(self):
        query = text(
            """
            SELECT
              wo.id AS order_id,
              c.name AS client_name,
              i.total AS invoice_total,
              COALESCE(SUM(DISTINCT wop.subtotal), 0) AS parts_cost,
              COALESCE(SUM(DISTINCT wot.price), 0) AS labor_cost,
              (i.total - COALESCE(SUM(DISTINCT wop.subtotal), 0) - COALESCE(SUM(DISTINCT wot.price), 0)) AS profit
            FROM work_orders wo
            JOIN invoices i ON i.work_order_id = wo.id
            JOIN clients c ON c.id = i.client_id
            LEFT JOIN work_order_parts wop ON wop.work_order_id = wo.id
            LEFT JOIN work_order_tasks wot ON wot.work_order_id = wo.id
            GROUP BY wo.id, c.name, i.total
            ORDER BY profit DESC;
        """
        )
        result = await self.db.execute(query)
        return [dict(row) for row in result.fetchall()]

    async def billing_by_client(self):
        query = text(
            """
            SELECT
              c.id AS client_id,
              c.name AS client_name,
              SUM(i.total) AS total_billed,
              SUM(i.paid) AS total_paid
            FROM invoices i
            JOIN clients c ON c.id = i.client_id
            GROUP BY c.id, c.name
            ORDER BY total_billed DESC;
        """
        )
        result = await self.db.execute(query)
        return [dict(row) for row in result.fetchall()]

    async def top_clients(self, limit: int = 5):
        query = text(
            """
            SELECT
              c.name AS client_name,
              SUM(i.total) AS total_billed
            FROM invoices i
            JOIN clients c ON c.id = i.client_id
            GROUP BY c.name
            ORDER BY total_billed DESC
            LIMIT :limit;
        """
        )
        result = await self.db.execute(query, {"limit": limit})
        return [dict(row) for row in result.fetchall()]

    async def income_monthly(self):
        query = text(
            """
            SELECT
              TO_CHAR(DATE_TRUNC('month', issued_at), 'YYYY-MM') AS month,
              SUM(total) AS total_income
            FROM invoices
            GROUP BY month
            ORDER BY month DESC;
        """
        )
        result = await self.db.execute(query)
        return [dict(row) for row in result.fetchall()]

    async def payments_by_method(self):
        query = text(
            """
            SELECT
              pm.name AS method,
              SUM(p.amount) AS total_received
            FROM payments p
            JOIN payment_methods pm ON pm.id = p.method_id
            GROUP BY pm.name
            ORDER BY total_received DESC;
        """
        )
        result = await self.db.execute(query)
        return [dict(row) for row in result.fetchall()]

    async def expenses_monthly(self):
        query = text(
            """
            SELECT
              TO_CHAR(DATE_TRUNC('month', date), 'YYYY-MM') AS month,
              SUM(amount) AS total_expense
            FROM expenses
            GROUP BY month
            ORDER BY month DESC;
        """
        )
        result = await self.db.execute(query)
        return [dict(row) for row in result.fetchall()]

    async def expenses_by_type(self):
        query = text(
            """
            SELECT
              et.name AS type,
              SUM(e.amount) AS total_amount
            FROM expenses e
            JOIN expense_types et ON et.id = e.expense_type_id
            GROUP BY et.name
            ORDER BY total_amount DESC;
        """
        )
        result = await self.db.execute(query)
        return [dict(row) for row in result.fetchall()]

    async def monthly_balance(self):
        query = text(
            """
            WITH income AS (
                SELECT DATE_TRUNC('month', issued_at) AS month, SUM(total) AS total_income
                FROM invoices
                GROUP BY month
            ),
            expense AS (
                SELECT DATE_TRUNC('month', date) AS month, SUM(amount) AS total_expense
                FROM expenses
                GROUP BY month
            )
            SELECT
              TO_CHAR(COALESCE(i.month, e.month), 'YYYY-MM') AS month,
              COALESCE(i.total_income, 0) AS income,
              COALESCE(e.total_expense, 0) AS expense,
              (COALESCE(i.total_income, 0) - COALESCE(e.total_expense, 0)) AS balance
            FROM income i
            FULL OUTER JOIN expense e ON i.month = e.month
            ORDER BY month DESC;
        """
        )
        result = await self.db.execute(query)
        return [dict(row) for row in result.fetchall()]
