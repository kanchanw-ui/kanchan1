from __future__ import annotations

import pandas as pd

from app.parsers.loader import ensure_required_columns, ParsedDocument
from app.parsers.schema import CANONICAL_COLUMNS, OPTIONAL_COLUMNS


def normalize_document(doc: ParsedDocument) -> pd.DataFrame:
    """
    Normalize uploaded document into canonical schema.

    - Renames common header variations to canonical names.
    - Attempts to coerce numerical columns to floats.
    """
    df = doc.dataframe.copy()

    canonical = ensure_required_columns(df, CANONICAL_COLUMNS)
    for canonical_name, candidates in OPTIONAL_COLUMNS.items():
        matches = [col for col in df.columns if col in candidates]
        if matches:
            canonical[canonical_name] = df[matches[0]]

    for column in ("quantity", "unit_price", "total"):
        canonical[column] = (
            canonical[column]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("$", "", regex=False)
        )
        canonical[column] = pd.to_numeric(
            canonical[column], errors="coerce"
        )

    canonical["line_id"] = canonical["line_id"].astype(str)
    canonical["description"] = canonical["description"].astype(str)

    return canonical

