from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np
import pandas as pd

from app.analysis.models import ComparisonFinding, ComparisonResult, ComparisonSummary


@dataclass
class ComparatorConfig:
    quantity_tolerance: float = 1e-6
    price_tolerance: float = 0.01
    total_tolerance: float = 0.01


def compare_documents(
    invoice_df: pd.DataFrame, po_df: pd.DataFrame, config: ComparatorConfig | None = None
) -> ComparisonResult:
    config = config or ComparatorConfig()
    findings: List[ComparisonFinding] = []

    invoice = invoice_df.copy().reset_index(drop=True)
    po = po_df.copy().reset_index(drop=True)

    invoice["row_number"] = invoice.index + 1
    po["row_number"] = po.index + 1

    findings.extend(_detect_duplicates(invoice))
    findings.extend(_detect_unusual_entries(invoice))

    merged = invoice.merge(
        po,
        on="line_id",
        how="outer",
        suffixes=("_invoice", "_po"),
        indicator=True,
    )

    rate_mismatches = 0
    quantity_mismatches = 0
    unmatched_invoice = 0
    unmatched_po = 0

    for _, row in merged.iterrows():
        merge_type = row["_merge"]
        if merge_type == "left_only":
            unmatched_invoice += 1
            findings.append(
                ComparisonFinding(
                    type="unmatched_invoice_line",
                    severity="high",
                    message=(
                        f"Invoice line {row['line_id']} ({row['description_invoice']}) "
                        "does not exist in the purchase order."
                    ),
                    invoice_rows=[int(row["row_number_invoice"])],
                )
            )
            continue
        if merge_type == "right_only":
            unmatched_po += 1
            findings.append(
                ComparisonFinding(
                    type="unmatched_po_line",
                    severity="medium",
                    message=(
                        f"Purchase order line {row['line_id']} ({row['description_po']}) "
                        "is missing on the invoice."
                    ),
                    po_rows=[int(row["row_number_po"])],
                )
            )
            continue

        invoice_row = int(row["row_number_invoice"])
        po_row = int(row["row_number_po"])

        quantity_invoice = row.get("quantity_invoice")
        quantity_po = row.get("quantity_po")

        if not _is_close(quantity_invoice, quantity_po, config.quantity_tolerance):
            quantity_mismatches += 1
            findings.append(
                ComparisonFinding(
                    type="quantity_mismatch",
                    severity="high",
                    message=(
                        f"Line {row['line_id']} quantity mismatch. "
                        f"Invoice: {quantity_invoice}, PO: {quantity_po}"
                    ),
                    invoice_rows=[invoice_row],
                    po_rows=[po_row],
                )
            )

        price_invoice = row.get("unit_price_invoice")
        price_po = row.get("unit_price_po")
        if not _is_close(price_invoice, price_po, config.price_tolerance):
            rate_mismatches += 1
            findings.append(
                ComparisonFinding(
                    type="rate_mismatch",
                    severity="high",
                    message=(
                        f"Line {row['line_id']} unit price mismatch. "
                        f"Invoice: {price_invoice}, PO: {price_po}"
                    ),
                    invoice_rows=[invoice_row],
                    po_rows=[po_row],
                )
            )

        total_invoice = row.get("total_invoice")
        total_po = row.get("total_po")
        if not _is_close(total_invoice, total_po, config.total_tolerance):
            findings.append(
                ComparisonFinding(
                    type="total_mismatch",
                    severity="medium",
                    message=(
                        f"Line {row['line_id']} total mismatch. "
                        f"Invoice: {total_invoice}, PO: {total_po}"
                    ),
                    invoice_rows=[invoice_row],
                    po_rows=[po_row],
                )
            )

    summary = ComparisonSummary(
        invoice_total=float(np.nansum(invoice["total"])),
        po_total=float(np.nansum(po["total"])),
        variance=float(np.nansum(invoice["total"]) - np.nansum(po["total"])),
        unmatched_invoice_lines=unmatched_invoice,
        unmatched_po_lines=unmatched_po,
        rate_mismatches=rate_mismatches,
        quantity_mismatches=quantity_mismatches,
        duplicates=_count_duplicate_rows(invoice),
    )

    return ComparisonResult(
        summary=summary,
        findings=findings,
        normalized_invoice=invoice,
        normalized_po=po,
    )


def _is_close(val_a, val_b, tol) -> bool:
    if pd.isna(val_a) and pd.isna(val_b):
        return True
    if pd.isna(val_a) or pd.isna(val_b):
        return False
    return abs(float(val_a) - float(val_b)) <= tol


def _detect_duplicates(df: pd.DataFrame) -> List[ComparisonFinding]:
    duplicates_mask = df.duplicated(subset=["line_id"], keep=False)
    findings: List[ComparisonFinding] = []
    if duplicates_mask.any():
        duplicate_rows = df[duplicates_mask]
        for line_id, group in duplicate_rows.groupby("line_id"):
            row_numbers = group["row_number"].astype(int).tolist()
            findings.append(
                ComparisonFinding(
                    type="duplicate_line",
                    severity="medium",
                    message=f"Duplicate invoice lines detected for line_id {line_id}",
                    invoice_rows=row_numbers,
                )
            )
    return findings


def _count_duplicate_rows(df: pd.DataFrame) -> int:
    return int(df.duplicated(subset=["line_id"], keep=False).sum())


def _detect_unusual_entries(df: pd.DataFrame) -> List[ComparisonFinding]:
    totals = df["total"].dropna()
    findings: List[ComparisonFinding] = []
    if totals.empty or len(totals) < 2:
        return findings

    mean = totals.mean()
    std = totals.std()
    if std == 0 or np.isnan(std):
        return findings

    threshold = mean + 2 * std
    unusual_rows = df[df["total"] > threshold]
    for _, row in unusual_rows.iterrows():
        findings.append(
            ComparisonFinding(
                type="unusual_amount",
                severity="medium",
                message=(
                    f"Invoice line {row['line_id']} total {row['total']} exceeds statistical threshold "
                    f"{threshold:.2f}."
                ),
                invoice_rows=[int(row["row_number"])],
                metadata={"threshold": threshold, "mean": mean, "std": std},
            )
        )
    return findings

