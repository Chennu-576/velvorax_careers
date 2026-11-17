from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class InvoiceItemSchema(BaseModel):
    description: str
    quantity: int = 1
    unit_price: float
    line_total: float

class InvoiceCreate(BaseModel):
    customer_name: str
    customer_email: str
    billing_address: Optional[str] = None
    company_id: Optional[int] = None
    currency: str = "INR"
    due_date: Optional[str] = None
    notes: Optional[str] = None
    items: List[InvoiceItemSchema]

class PaymentResponse(BaseModel):
    id: int
    invoice_id: int
    transaction_ref: str
    payment_provider: str
    amount: float
    currency: str
    status: str
    payment_method: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    company_id: Optional[int] = None
    customer_name: str
    customer_email: str
    billing_address: Optional[str] = None
    currency: str
    subtotal: float
    tax_amount: float
    total_amount: float
    status: str
    due_date: Optional[str] = None
    issued_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    items: List[InvoiceItemSchema] = []
    payments: List[PaymentResponse] = []

    class Config:
        from_attributes = True
