from pathlib import Path
from typing import Any, BinaryIO
import pandas as pd

def read_csv_safely(source: str | Path | BinaryIO) -> pd.DataFrame:
    """Read CSV using common encoding fallbacks and validate its columns."""
    errors = []
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            if hasattr(source, "seek"):
                source.seek(0)
            frame = pd.read_csv(source, encoding=encoding)
            if len(frame.columns) == 0:
                raise ValueError("CSV has no columns.")
            frame.columns = [str(c).strip() for c in frame.columns]
            if any(not c for c in frame.columns):
                raise ValueError("Column names cannot be blank.")
            if frame.columns.duplicated().any():
                raise ValueError("Duplicate column names are not supported.")
            return frame
        except Exception as exc:
            errors.append(f"{encoding}: {exc}")
    raise ValueError("Unable to parse CSV. " + " | ".join(errors))

def profile_dataset(df: pd.DataFrame) -> dict[str, Any]:
    """Return dataset dimensions, quality metrics, and per-column profiles."""
    columns = []
    for name in df.columns:
        series = df[name]
        samples = series.dropna().astype(str).head(3).tolist()
        columns.append({
            "column": str(name), "dtype": str(series.dtype),
            "non_null": int(series.notna().sum()), "missing": int(series.isna().sum()),
            "missing_pct": round(float(series.isna().mean() * 100), 2),
            "unique": int(series.nunique(dropna=True)), "sample_values": ", ".join(samples)
        })
    numeric = df.select_dtypes(include="number")
    return {
        "rows": int(len(df)), "columns": int(len(df.columns)),
        "missing_cells": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "column_profiles": columns,
        "numeric_summary": numeric.describe().round(3).to_dict() if not numeric.empty else {}
    }

def build_insights(df: pd.DataFrame, profile: dict[str, Any] | None = None) -> list[str]:
    """Generate deterministic observations without an LLM."""
    profile = profile or profile_dataset(df)
    notes = []
    if profile["missing_cells"]:
        affected = sum(1 for c in profile["column_profiles"] if c["missing"] > 0)
        notes.append(f"{profile['missing_cells']} missing cells across {affected} columns.")
    else:
        notes.append("No missing cells were found.")
    if profile["duplicate_rows"]:
        notes.append(f"{profile['duplicate_rows']} duplicate rows were found.")
    else:
        notes.append("No duplicate rows were found.")
    for col in df.select_dtypes(include="number").columns:
        values = df[col].dropna()
        if not values.empty:
            notes.append(f"{col}: mean {values.mean():,.2f}; min {values.min():,.2f}; max {values.max():,.2f}.")
    numeric_cols = df.select_dtypes(include="number").columns
    categorical = [c for c in df.columns if c not in numeric_cols and 1 < df[c].nunique(dropna=True) <= 30]
    for col in categorical[:3]:
        counts = df[col].value_counts(dropna=True)
        if not counts.empty:
            notes.append(f"{col}: most frequent value is '{counts.index[0]}' ({int(counts.iloc[0])} rows).")
    return notes

def build_analysis_context(df: pd.DataFrame, profile: dict[str, Any], insights: list[str]) -> str:
    """Create compact context from aggregate data only; do not include raw rows."""
    numeric = df.select_dtypes(include="number")
    numeric_summary = numeric.describe().round(2).to_string() if not numeric.empty else "No numeric columns."
    categorical_parts = []
    for col in df.columns:
        if col not in numeric.columns and df[col].nunique(dropna=True) <= 30:
            categorical_parts.append(f"{col}: {df[col].value_counts(dropna=True).head(10).to_dict()}")
    return (
        f"Rows: {profile['rows']}\nColumns: {list(map(str, df.columns))}\n"
        f"Missing cells: {profile['missing_cells']}\nDuplicate rows: {profile['duplicate_rows']}\n"
        f"Numeric summary:\n{numeric_summary}\nCategorical summaries:\n"
        + "\n".join(categorical_parts) + "\nAutomated observations:\n- " + "\n- ".join(insights)
    )
