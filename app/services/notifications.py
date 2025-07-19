import logging
from typing import Iterable

from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.roles import ADMIN
from app.db.repositories.users import UsersRepository
from app.models.invoices import BankCheck


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.users_repo = UsersRepository(db)

    async def _send_email(
        self, recipients: Iterable[str], subject: str, body: str
    ) -> None:
        logging.info(
            "Sending email to %s: %s - %s", ", ".join(recipients), subject, body
        )

    async def notify_due_check(self, check: BankCheck) -> None:
        admins = await self.users_repo.list(role_id=ADMIN)
        recipients = [a.email for a in admins]
        invoice = check.payment.invoice if check.payment else None
        if invoice and invoice.work_order and invoice.work_order.reviewer:
            recipients.append(invoice.work_order.reviewer.email)
        subject = "Cheque próximo a vencer"
        body = f"El cheque {check.check_number} vence el {check.due_date}"
        await self._send_email(recipients, subject, body)
