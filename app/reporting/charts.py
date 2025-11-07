from __future__ import annotations

import altair as alt
import pandas as pd

from app.analysis.models import ComparisonResult


def summary_bar_chart(result: ComparisonResult) -> alt.Chart:
    data = pd.DataFrame(
        [
            {"metric": "Unmatched Invoice Lines", "value": result.summary.unmatched_invoice_lines},
            {"metric": "Unmatched PO Lines", "value": result.summary.unmatched_po_lines},
            {"metric": "Rate Mismatches", "value": result.summary.rate_mismatches},
            {"metric": "Quantity Mismatches", "value": result.summary.quantity_mismatches},
            {"metric": "Duplicates", "value": result.summary.duplicates},
        ]
    )

    chart = (
        alt.Chart(data)
        .mark_bar(color="#6366f1")
        .encode(
            x=alt.X("metric:N", sort="-y", title="Issue Type"),
            y=alt.Y("value:Q", title="Count"),
            tooltip=["metric", "value"],
        )
        .properties(width="container", height=320, title="Discrepancy Summary")
    )
    return chart


def totals_compare_chart(result: ComparisonResult) -> alt.Chart:
    data = pd.DataFrame(
        [
            {"category": "Invoice", "total": result.summary.invoice_total},
            {"category": "Purchase Order", "total": result.summary.po_total},
        ]
    )
    chart = (
        alt.Chart(data)
        .mark_bar(color="#22c55e")
        .encode(
            x=alt.X("category:N", title="Document"),
            y=alt.Y("total:Q", title="Total Amount"),
            tooltip=["category", alt.Tooltip("total:Q", format=",.2f")],
        )
        .properties(width="container", height=240, title="Total Comparison")
    )
    return chart

