from __future__ import annotations

import io
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

import numpy as np
import pandas as pd
import pdfplumber

from app.utils import normalize_headers


SUPPORTED_EXTENSIONS = {".csv", ".xls", ".xlsx", ".xlsm", ".pdf"}


class UnsupportedFileTypeError(ValueError):
    """Raised when an uploaded file cannot be parsed."""


@dataclass
class ParsedDocument:
    """Container for a parsed invoice or purchase order table."""

    source_name: str
    dataframe: pd.DataFrame


def detect_extension(filename: str) -> str:
    lower = filename.lower()
    for ext in SUPPORTED_EXTENSIONS:
        if lower.endswith(ext):
            return ext
    raise UnsupportedFileTypeError(f"Unsupported file type for {filename}")


def read_table(file_bytes: bytes, filename: str) -> ParsedDocument:
    """
    Load tabular data from the supported invoice/PO document.

    Excel/CSV files rely on pandas. PDF files are parsed using pdfplumber and the
    first table conglomerated across pages is returned.
    """
    extension = detect_extension(filename)
    if extension in {".csv"}:
        df = pd.read_csv(io.BytesIO(file_bytes))
    elif extension in {".xls", ".xlsx", ".xlsm"}:
        df = pd.read_excel(io.BytesIO(file_bytes))
    elif extension == ".pdf":
        df = _read_table_from_pdf(file_bytes, filename)
    else:
        raise UnsupportedFileTypeError(f"No reader implemented for {filename}")

    df.columns = normalize_headers(df.columns)
    df = df.replace({np.nan: None})
    return ParsedDocument(source_name=filename, dataframe=df)


def _read_table_from_pdf(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """Attempt to extract the most relevant table from a PDF."""
    tables: List[pd.DataFrame] = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            extracted_tables = page.extract_tables()
            for raw_table in extracted_tables:
                if not raw_table:
                    continue
                df = pd.DataFrame(raw_table[1:], columns=normalize_headers(raw_table[0]))
                tables.append(df)

    if not tables:
        raise UnsupportedFileTypeError(
            f"No tables found in PDF document {filename}. Please upload a tabular invoice/PO."
        )

    # Heuristic: pick the table with the most rows
    tables.sort(key=lambda table: table.shape[0], reverse=True)
    return tables[0]


def ensure_required_columns(
    df: pd.DataFrame, possible_columns: Dict[str, Iterable[str]]
) -> pd.DataFrame:
    """
    Ensure the dataframe contains the canonical columns defined in possible_columns.

    possible_columns maps canonical field names to a list of acceptable column headers.
    If a canonical column cannot be found, an informative error is raised.
    """
    column_map: Dict[str, Optional[str]] = {}

    for canonical, options in possible_columns.items():
        matches = [col for col in df.columns if col in options]
        if matches:
            column_map[canonical] = matches[0]
        else:
            column_map[canonical] = None

    missing = [key for key, value in column_map.items() if value is None]
    if missing:
        raise ValueError(
            f"Missing expected columns {missing}. Detected columns: {list(df.columns)}"
        )

    renamed = df.rename(columns={original: canonical for canonical, original in column_map.items()})
    return renamed

