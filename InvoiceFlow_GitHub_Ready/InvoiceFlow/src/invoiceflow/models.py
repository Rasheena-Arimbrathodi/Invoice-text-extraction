from typing import List, Optional
from pydantic import BaseModel, Field


class LineItem(BaseModel):
    description: str
    quantity: float = 1.0
    unit_price: float
    amount: float


class ValidationReport(BaseModel):
    is_math_valid: bool
    line_items_sum: float
    expected_total: Optional[float] = None
    discrepancy: float = 0.0
    warnings: List[str] = Field(default_factory=list)


class InvoiceData(BaseModel):
    vendor_name: str = "Unknown Vendor"
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    currency: str = "USD"
    line_items: List[LineItem] = Field(default_factory=list)
    subtotal: Optional[float] = None
    tax_amount: float = 0.0
    total_amount: Optional[float] = None
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    validation: ValidationReport
    raw_text_preview: str = ""


class TextExtractionRequest(BaseModel):
    text: str = Field(..., min_length=5, description="Raw OCR or PDF invoice text")
    source_name: str = Field(default="raw_text")
