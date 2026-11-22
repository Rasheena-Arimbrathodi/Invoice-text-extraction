from invoiceflow.parser import InvoiceParser


def test_validator_detects_total_mismatch():
    broken_invoice = """
    Test Corp
    Invoice Number: INV-999
    Invoice Date: 2026-11-01
    Widget A | 2 | $50.00 | $100.00
    Subtotal: $100.00
    Tax (10%): $10.00
    Total Due: $150.00
    """
    inv = InvoiceParser().parse(broken_invoice)
    assert inv.validation.is_math_valid is False
    assert inv.validation.discrepancy == 40.0
    assert len(inv.validation.warnings) >= 1
    assert inv.confidence_score < 1.0
