import re
from typing import List, Optional
from invoiceflow.models import InvoiceData, LineItem
from invoiceflow.validator import validate_invoice

CURRENCY_PATTERNS = [
    (r"\bINR\b|₹", "INR"),
    (r"\bEUR\b|€", "EUR"),
    (r"\bGBP\b|£", "GBP"),
    (r"\bUSD\b|\$", "USD"),
]

INVOICE_NUM_PATTERNS = [
    re.compile(r"(?:Invoice\s*(?:Number|No\.?|#))\s*[:#\-]?\s*([A-Z0-9\-\/]+)", re.IGNORECASE),
    re.compile(r"\b(INV[\-\/][A-Z0-9\-\/]+)\b", re.IGNORECASE),
]

DATE_PATTERN = r"(\d{4}-\d{2}-\d{2}|\d{2}[\/\-]\d{2}[\/\-]\d{4})"
INVOICE_DATE_RE = re.compile(rf"(?:Invoice\s*Date|Issued|Date)\s*[:\-]?\s*{DATE_PATTERN}", re.IGNORECASE)
DUE_DATE_RE = re.compile(rf"(?:Due\s*Date|Payment\s*Due)\s*[:\-]?\s*{DATE_PATTERN}", re.IGNORECASE)

MONEY_RE = r"(?:USD|INR|EUR|GBP|\$|₹|€|£)?\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{1,2})?|[0-9]+(?:\.[0-9]{1,2})?)"
SUBTOTAL_RE = re.compile(rf"(?:Subtotal|Sub\s*Total)\s*[:\-]?\s*{MONEY_RE}", re.IGNORECASE)
TAX_RE = re.compile(rf"(?:Tax|VAT|GST)(?:\s*\([^)]+\))?\s*[:\-]?\s*{MONEY_RE}", re.IGNORECASE)
TOTAL_RE = re.compile(rf"(?:Grand\s*Total|Total\s*Due|Total\s*Amount|Balance\s*Due|Total)\s*[:\-]?\s*{MONEY_RE}", re.IGNORECASE)

PIPE_ITEM_RE = re.compile(
    rf"^(.+?)\s*\|\s*(\d+(?:\.\d+)?)\s*\|\s*{MONEY_RE}\s*\|\s*{MONEY_RE}\s*$"
)
SPACE_ITEM_RE = re.compile(
    rf"^([A-Za-z][A-Za-z0-9\s\-\(\)\/&]+?)\s{{2,}}(\d+(?:\.\d+)?)\s+{MONEY_RE}\s+{MONEY_RE}\s*$"
)


def _to_float(num_str: Optional[str]) -> Optional[float]:
    if not num_str:
        return None
    return round(float(num_str.replace(",", "")), 2)


class InvoiceParser:
    """Parses unstructured invoice text into a validated InvoiceData schema."""

    def detect_currency(self, text: str) -> str:
        for pattern, code in CURRENCY_PATTERNS:
            if re.search(pattern, text):
                return code
        return "USD"

    def extract_vendor(self, lines: List[str]) -> str:
        skip_keywords = ("invoice", "tax invoice", "bill to", "date", "receipt")
        for line in lines[:5]:
            lower = line.lower().strip()
            if lower and not any(lower.startswith(k) for k in skip_keywords):
                return line.strip()
        return "Unknown Vendor"

    def extract_line_items(self, lines: List[str]) -> List[LineItem]:
        items: List[LineItem] = []
        for raw in lines:
            line = raw.strip()
            if not line or line.lower().startswith(("description", "item |", "item ")):
                continue
            match = PIPE_ITEM_RE.match(line) or SPACE_ITEM_RE.match(line)
            if match:
                desc, qty_s, unit_s, amt_s = match.groups()
                qty = float(qty_s)
                unit_price = _to_float(unit_s) or 0.0
                amount = _to_float(amt_s) or round(qty * unit_price, 2)
                items.append(
                    LineItem(
                        description=desc.strip(),
                        quantity=qty,
                        unit_price=unit_price,
                        amount=amount,
                    )
                )
        return items

    def parse(self, text: str) -> InvoiceData:
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        currency = self.detect_currency(text)
        vendor = self.extract_vendor(lines)

        invoice_number: Optional[str] = None
        for pat in INVOICE_NUM_PATTERNS:
            m = pat.search(text)
            if m:
                invoice_number = m.group(1).strip()
                break

        inv_date_m = INVOICE_DATE_RE.search(text)
        due_date_m = DUE_DATE_RE.search(text)
        invoice_date = inv_date_m.group(1) if inv_date_m else None
        due_date = due_date_m.group(1) if due_date_m else None

        line_items = self.extract_line_items(lines)

        sub_m = SUBTOTAL_RE.search(text)
        tax_m = TAX_RE.search(text)
        tot_m = TOTAL_RE.search(text)

        subtotal = _to_float(sub_m.group(1)) if sub_m else None
        tax_amount = (_to_float(tax_m.group(1)) if tax_m else 0.0) or 0.0
        total_amount = _to_float(tot_m.group(1)) if tot_m else None

        if subtotal is None and line_items:
            subtotal = round(sum(it.amount for it in line_items), 2)

        validation, confidence = validate_invoice(
            vendor_name=vendor,
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            line_items=line_items,
            subtotal=subtotal,
            tax_amount=tax_amount,
            total_amount=total_amount,
        )

        return InvoiceData(
            vendor_name=vendor,
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            due_date=due_date,
            currency=currency,
            line_items=line_items,
            subtotal=subtotal,
            tax_amount=tax_amount,
            total_amount=total_amount,
            confidence_score=confidence,
            validation=validation,
            raw_text_preview=text[:240].strip(),
        )
