"""
Tests for the preprocessing pipeline.

These tests validate that the Hillstrom preprocessing step produces
a clean and analysis-ready dataset with the expected structure.
"""

from __future__ import annotations

import pandas as pd

from conversion_uplift.preprocess import preprocess_data


def test_preprocess_data_returns_dataframe() -> None:
    """
    Test that preprocess_data returns a pandas DataFrame.
    """
    df = preprocess_data()
    assert isinstance(df, pd.DataFrame)


def test_preprocess_data_has_expected_columns() -> None:
    """
    Test that the processed dataset contains the expected output columns.
    """
    df = preprocess_data()

    expected_columns = [
        "customer_id",
        "recency",
        "history_segment",
        "history",
        "mens",
        "womens",
        "zip_code",
        "newbie",
        "channel",
        "segment",
        "campaign_type",
        "binary_treatment_flag",
        "visit",
        "conversion",
        "spend",
    ]

    assert list(df.columns) == expected_columns


def test_binary_treatment_flag_contains_only_zero_and_one() -> None:
    """
    Test that binary_treatment_flag contains only valid binary values.
    """
    df = preprocess_data()
    unique_values = set(df["binary_treatment_flag"].unique())

    assert unique_values.issubset({0, 1})


def test_customer_id_starts_at_one_and_is_unique() -> None:
    """
    Test that customer_id starts at 1 and is unique for each row.
    """
    df = preprocess_data()

    assert df["customer_id"].iloc[0] == 1
    assert df["customer_id"].is_unique


def test_no_invalid_zip_code_values_remain() -> None:
    """
    Test that zip_code contains only the cleaned expected values.
    """
    df = preprocess_data()
    valid_zip_codes = {"Urban", "Rural", "Suburban"}

    assert set(df["zip_code"].unique()).issubset(valid_zip_codes)


def test_campaign_type_matches_segment_logic() -> None:
    """
    Test that campaign_type is created consistently from segment values.
    """
    df = preprocess_data()

    mapping = {
        "Mens E-Mail": "mens_email",
        "Womens E-Mail": "womens_email",
        "No E-Mail": "control",
    }

    expected_campaign_type = df["segment"].map(mapping)

    assert (df["campaign_type"] == expected_campaign_type).all()