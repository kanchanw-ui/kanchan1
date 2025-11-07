from __future__ import annotations

import io
from typing import Iterable, List

import pandas as pd


def normalize_headers(headers: Iterable[str]) -> List[str]:
    """Normalize dataframe headers for comparison."""
    normalized = []
    for header in headers:
        normalized.append(
            header.strip().lower().replace(" ", "_").replace("-", "_")
        )
    return normalized


def dataframe_to_csv_buffer(df: pd.DataFrame) -> io.BytesIO:
    """Serialize a dataframe to an in-memory CSV buffer."""
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer

