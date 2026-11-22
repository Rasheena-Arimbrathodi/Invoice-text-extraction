from pathlib import Path
from invoiceflow.extractor import DocumentIngestor
from invoiceflow.parser import InvoiceParser


def test_parse_usd_invoice():
    data_file = Path(__file__).resolve().parents[1] / "data" / "sample_invoice_01.txt"
    text = DocumentIngestor().extract_from_path(data_file)
    inv = InvoiceParser().parse(text)

    assert inv.vendor_name == "ACME CLOUD SERVICES INC."
    assert inv.invoice_number == "INV-2026-1042"
    assert inv.invoice_date == "2026-10-15"
    assert inv.due_date == "2026-11-14"
    assert inv.currency == "USD"
    assert len(inv.line_items) == 3
    assert inv.subtotal == 1200.00
    assert inv.tax_amount == 120.00
    assert inv.total_amount == 1320.00
    assert inv.validation.is_math_valid is True
    assert inv.confidence_score == 1.0


def test_parse_inr_invoice():
    data_file = Path(__file__).resolve().parents[1] / "data" / "sample_invoice_02.txt"
    text = DocumentIngestor().extract_from_path(data_file)
    inv = InvoiceParser().parse(text)

    assert inv.invoice_number == "BLF/26-27/0891"
    assert inv.currency == "INR"
    assert inv.subtotal == 15000.00
    assert inv.tax_amount == 2700.00
    assert inv.total_amount == 17700.00
    assert inv.validation.is_math_valid is True
