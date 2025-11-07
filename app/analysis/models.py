from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class LineItemSummary(BaseModel):
    line_id: str
    description: str
    quantity: Optional[float]
    unit_price: Optional[float]
    total: Optional[float]
    source: str = Field(description="Either 'invoice' or 'po'")
    row_number: Optional[int] = None


class ComparisonFinding(BaseModel):
    type: str
    severity: str
    message: str
    invoice_rows: List[int] = Field(default_factory=list)
    po_rows: List[int] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ComparisonSummary(BaseModel):
    invoice_total: float
    po_total: float
    variance: float
    unmatched_invoice_lines: int
    unmatched_po_lines: int
    rate_mismatches: int
    quantity_mismatches: int
    duplicates: int


class ComparisonResult(BaseModel):
    summary: ComparisonSummary
    findings: List[ComparisonFinding]
    normalized_invoice: Any
    normalized_po: Any

    model_config = ConfigDict(arbitrary_types_allowed=True)

