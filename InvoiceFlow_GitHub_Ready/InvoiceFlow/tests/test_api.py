from fastapi.testclient import TestClient
from invoiceflow.api import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_extract_text_endpoint():
    sample = """
    Orion Labs
    Invoice Number: INV-500
    Invoice Date: 2026-11-20
    Consulting | 2 | $200.00 | $400.00
    Subtotal: $400.00
    Tax: $40.00
    Total Due: $440.00
    """
    resp = client.post("/extract/text", json={"text": sample})
    assert resp.status_code == 200
    body = resp.json()
    assert body["invoice_number"] == "INV-500"
    assert body["total_amount"] == 440.0
    assert body["validation"]["is_math_valid"] is True


def test_extract_file_upload():
    content = b"Alpha Co\nInvoice Number: INV-88\nInvoice Date: 2026-11-22\nService | 1 | $100.00 | $100.00\nSubtotal: $100.00\nTax: $0.00\nTotal: $100.00"
    resp = client.post(
        "/extract/file",
        files={"file": ("invoice.txt", content, "text/plain")},
    )
    assert resp.status_code == 200
    assert resp.json()["invoice_number"] == "INV-88"


def test_evaluate_endpoint():
    resp = client.get("/evaluate")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 3
    assert body["passed"] == 3
    assert body["accuracy"] == 1.0
