from typing import List, Optional, Tuple
from invoiceflow.models import LineItem, ValidationReport


def validate_invoice(
    vendor_name: str,
    invoice_number: Optional[str],
    invoice_date: Optional[str],
    line_items: List[LineItem],
    subtotal: Optional[float],
    tax_amount: float,
    total_amount: Optional[float],
) -> Tuple[ValidationReport, float]:
    """Cross-checks extracted invoice arithmetic and computes a confidence score."""
    warnings: List[str] = []
    items_sum = round(sum(item.amount for item in line_items), 2)

    for item in line_items:
        expected_line = round(item.quantity * item.unit_price, 2)
        if abs(expected_line - item.amount) > 0.02:
            warnings.append(
                f"Line item '{item.description}' qty*price ({expected_line}) != amount ({item.amount})"
            )

    base_amount = items_sum if line_items else (subtotal or 0.0)
    if line_items and subtotal is not None and abs(items_sum - subtotal) > 0.02:
        warnings.append(f"Line items sum ({items_sum}) differs from subtotal ({subtotal})")

    expected_total = round(base_amount + tax_amount, 2) if (base_amount or total_amount is not None) else None
    discrepancy = 0.0
    is_math_valid = True

    if total_amount is not None and expected_total is not None:
        discrepancy = round(abs(total_amount - expected_total), 2)
        if discrepancy > 0.02:
            is_math_valid = False
            warnings.append(
                f"Extracted total ({total_amount}) does not match subtotal+tax ({expected_total})"
            )
    elif total_amount is None:
        is_math_valid = False
        warnings.append("Missing total_amount")

    # Compute calibrated confidence score
    score = 0.0
    if vendor_name and vendor_name != "Unknown Vendor":
        score += 0.15
    if invoice_number:
        score += 0.20
    if invoice_date:
        score += 0.15
    if line_items:
        score += 0.20
    if total_amount is not None:
        score += 0.15
    if is_math_valid and not warnings:
        score += 0.15

    report = ValidationReport(
        is_math_valid=is_math_valid,
        line_items_sum=items_sum,
        expected_total=expected_total,
        discrepancy=discrepancy,
        warnings=warnings,
    )
    return report, round(min(score, 1.0), 4)
