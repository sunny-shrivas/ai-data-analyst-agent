from io import BytesIO
import pandas as pd
import pytest
from tools import build_analysis_context, build_insights, profile_dataset, read_csv_safely

def sample_frame():
    return pd.DataFrame({"Region": ["North", "South", "North", "South"], "Sales": [100.0, 80.0, 120.0, None]})

def test_read_csv_safely_reads_bytes():
    frame = read_csv_safely(BytesIO(b"region,sales\nNorth,100\nSouth,80\n"))
    assert frame.shape == (2, 2)
    assert frame.columns.tolist() == ["region", "sales"]

def test_profile_counts_missing_and_duplicates():
    frame = pd.DataFrame({"x": [1, 1, None], "y": ["a", "a", "b"]})
    profile = profile_dataset(frame)
    assert profile["rows"] == 3
    assert profile["columns"] == 2
    assert profile["missing_cells"] == 1
    assert profile["duplicate_rows"] == 1

def test_insights_include_numeric_and_categorical_observations():
    frame = sample_frame()
    insights = build_insights(frame)
    assert any("missing cells" in x.lower() for x in insights)
    assert any("Sales" in x for x in insights)
    assert any("Region" in x for x in insights)

def test_context_uses_aggregates_not_raw_rows():
    frame = sample_frame()
    profile = profile_dataset(frame)
    context = build_analysis_context(frame, profile, build_insights(frame, profile))
    assert "Rows: 4" in context
    assert "Sales" in context
    assert "North, 100" not in context

def test_empty_csv_is_rejected():
    with pytest.raises(ValueError):
        read_csv_safely(BytesIO(b""))
