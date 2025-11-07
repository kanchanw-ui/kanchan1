from __future__ import annotations

from typing import Dict, Iterable, List, Mapping


CANONICAL_COLUMNS: Dict[str, List[str]] = {
    "line_id": ["line_id", "item", "item_id", "line", "sku", "product_code"],
    "description": ["description", "item_description", "details"],
    "quantity": ["quantity", "qty", "ordered_qty", "billed_quantity"],
    "unit_price": ["unit_price", "price", "unit_cost", "rate"],
    "total": ["amount", "total", "line_total", "extended_price", "cost"],
}

OPTIONAL_COLUMNS: Mapping[str, Iterable[str]] = {
    "uom": ["uom", "unit", "unit_of_measure"],
    "tax": ["tax", "tax_amount", "tax_total"],
    "po_number": ["po_number", "po", "purchase_order"],
}

