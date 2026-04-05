"""
Tests for raw data ingestion utilities in the conversion uplift project.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from conversion_uplift.ingest import (
    EXPECTED_RAW_COLUMNS,
    get_raw_data_path,
    load_raw_data,
    validate_raw_columns,
)


def make_valid_raw_df() -> pd.DataFrame:
    """
    Build a small valid raw dataset for testing.
    """
    return pd.DataFrame(
        {
            "recency": [1, 2],
            "history_segment": ["1) $0 - $100", "2) $100 - $200"],
            "history": [42.0, 110.5],
            "mens": [1, 0],
            "womens": [0, 1],
            "zip_code": ["Urban", "Suburban"],
            "newbie": [1, 0],
            "channel": ["Web", "Phone"],
            "segment": ["Mens E-Mail", "No E-Mail"],
            "visit": [1, 0],
            "conversion": [0, 1],
            "spend": [0.0, 15.0],
        }
    )


def test_get_raw_data_path_points_to_hillstrom_csv() -> None:
    """
    The raw data path helper should point to hillstrom.csv.
    """
    path = get_raw_data_path()

    assert isinstance(path, Path)
    assert path.name == "hillstrom.csv"


def test_load_raw_data_reads_csv_file(tmp_path: Path) -> None:
    """
    Loading raw data should return the contents of a valid CSV file.
    """
    df = make_valid_raw_df()
    file_path = tmp_path / "sample_raw.csv"
    df.to_csv(file_path, index=False)

    result = load_raw_data(file_path=file_path)

    pd.testing.assert_frame_equal(result, df)


def test_load_raw_data_raises_file_not_found_for_missing_file(tmp_path: Path) -> None:
    """
    Loading raw data should raise FileNotFoundError for a missing file.
    """
    missing_path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError, match="Raw data file not found"):
        load_raw_data(file_path=missing_path)


def test_validate_raw_columns_accepts_valid_schema() -> None:
    """
    Raw column validation should pass for a valid raw dataset.
    """
    df = make_valid_raw_df()

    validate_raw_columns(df)


def test_validate_raw_columns_raises_for_missing_required_columns() -> None:
    """
    Raw column validation should fail if required columns are missing.
    """
    df = make_valid_raw_df().drop(columns=["spend", "channel"])

    with pytest.raises(ValueError, match="Raw dataset is missing required columns"):
        validate_raw_columns(df)


def test_validate_raw_columns_all_expected_columns_are_present_in_valid_fixture() -> None:
    """
    The valid fixture should contain exactly the required raw columns.
    """
    df = make_valid_raw_df()

    assert set(EXPECTED_RAW_COLUMNS).issubset(df.columns)
    assert len(df.columns) == len(EXPECTED_RAW_COLUMNS)


def test_validate_raw_columns_allows_extra_columns_without_failing() -> None:
    """
    Extra columns should not cause validation failure.
    """
    df = make_valid_raw_df().copy()
    df["extra_column"] = ["x", "y"]

    validate_raw_columns(df)