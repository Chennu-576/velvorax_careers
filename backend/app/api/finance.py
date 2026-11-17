import uuid
from typing import Optional, List, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.permissions import require_admin
from app.models.user import User
from app.models.finance import Invoice, InvoiceItem, Payment
from app.schemas.finance import InvoiceCreate, InvoiceResponse, PaymentResponse

router = APIRouter(prefix="/admin/finance", tags=["Finance & Billing"])

class FinancialSummary(BaseModel):
    total_invoiced: float
    total_paid: float
    total_pending: float
    invoices_count: int
    payments_count: int

@router.get("/summary", response_model=FinancialSummary)
async def get_financial_summary(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    invoices_count = (await db.execute(select(func.count(Invoice.id)))).scalar_one()
    payments_count = (await db.execute(select(func.count(Payment.id)))).scalar_one()

    total_invoiced = (await db.execute(select(func.coalesce(func.sum(Invoice.total_amount), 0.0)))).scalar_one()
    total_paid = (await db.execute(select(func.coalesce(func.sum(Payment.amount), 0.0)).where(Payment.status == "SUCCESSFUL"))).scalar_one()
    total_pending = max(0.0, total_invoiced - total_paid)

    return FinancialSummary(
        total_invoiced=total_invoiced,
        total_paid=total_paid,
        total_pending=total_pending,
        invoices_count=invoices_count,
        payments_count=payments_count
    )

@router.get("/invoices", response_model=List[InvoiceResponse])
async def list_invoices(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = (
        select(Invoice)
        .options(selectinload(Invoice.items), selectinload(Invoice.payments))
        .order_by(desc(Invoice.created_at))
    )
    invoices = (await db.execute(stmt)).scalars().all()
    return [InvoiceResponse.model_validate(inv) for inv in invoices]

@router.post("/invoices", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    payload: InvoiceCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    inv_num = f"INV-{datetime.now(timezone.utc).strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"

    subtotal = sum(item.line_total for item in payload.items)
    tax_amount = round(subtotal * 0.18, 2)  # 18% GST standard
    total_amount = subtotal + tax_amount

    invoice = Invoice(
        invoice_number=inv_num,
        company_id=payload.company_id,
        customer_name=payload.customer_name,
        customer_email=payload.customer_email,
        billing_address=payload.billing_address,
        currency=payload.currency,
        subtotal=subtotal,
        tax_amount=tax_amount,
        total_amount=total_amount,
        status="ISSUED",
        due_date=payload.due_date,
        issued_at=datetime.now(timezone.utc),
        notes=payload.notes
    )
    db.add(invoice)
    await db.flush()

    for item in payload.items:
        inv_item = InvoiceItem(
            invoice_id=invoice.id,
            description=item.description,
            quantity=item.quantity,
            unit_price=item.unit_price,
            line_total=item.line_total
        )
        db.add(inv_item)

    await db.commit()

    # Reload invoice
    stmt = select(Invoice).where(Invoice.id == invoice.id).options(selectinload(Invoice.items), selectinload(Invoice.payments))
    loaded = (await db.execute(stmt)).scalar_one()
    return InvoiceResponse.model_validate(loaded)

@router.get("/payments", response_model=List[PaymentResponse])
async def list_payments(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(Payment).order_by(desc(Payment.created_at))
    payments = (await db.execute(stmt)).scalars().all()
    return [PaymentResponse.model_validate(p) for p in payments]
