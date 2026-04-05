"""
Tests for feature preparation utilities in the conversion uplift project.
"""

from __future__ import annotations

import pandas as pd

from conversion_uplift.features import (
    CATEGORICAL_FEATURE_COLUMNS,
    NUMERIC_FEATURE_COLUMNS,
    TARGET_COLUMNS,
    build_feature_matrix,
    build_feature_summary,
    build_modeling_base_dataset,
    build_target_dataframe,
)


def make_sample_processed_df() -> pd.DataFrame:
    """
    Build a small representative processed dataset for testing.
    """
    return pd.DataFrame(
        {
            "customer_id": [1, 2, 3, 4],
            "recency": [1, 4, 7, 10],
            "history_segment": [
                "1) $0 - $100",
                "2) $100 - $200",
                "3) $200 - $350",
                "1) $0 - $100",
            ],
            "history": [42.0, 130.5, 280.0, 95.0],
            "mens": [1, 0, 1, 0],
            "womens": [0, 1, 0, 1],
            "zip_code": ["Urban", "Suburban", "Rural", "Urban"],
            "newbie": [1, 0, 1, 0],
            "channel": ["Web", "Phone", "Multichannel", "Web"],
            "segment": ["Mens E-Mail", "No E-Mail", "Womens E-Mail", "No E-Mail"],
            "campaign_type": ["mens_email", "control", "womens_email", "control"],
            "binary_treatment_flag": [1, 0, 1, 0],
            "visit": [1, 0, 1, 0],
            "conversion": [0, 0, 1, 0],
            "spend": [0.0, 0.0, 25.0, 0.0],
        }
    )


def test_build_modeling_base_dataset_contains_expected_columns() -> None:
    """
    The modeling base dataset should include identifiers, features, and targets.
    """
    processed_df = make_sample_processed_df()

    result = build_modeling_base_dataset(processed_df)

    expected_columns = [
        "customer_id",
        "segment",
        *NUMERIC_FEATURE_COLUMNS,
        *CATEGORICAL_FEATURE_COLUMNS,
        *TARGET_COLUMNS,
    ]

    assert list(result.columns) == expected_columns
    assert len(result) == len(processed_df)


def test_build_modeling_base_dataset_preserves_target_values() -> None:
    """
    The base modeling dataset should preserve the target columns exactly.
    """
    processed_df = make_sample_processed_df()

    result = build_modeling_base_dataset(processed_df)

    pd.testing.assert_series_equal(result["visit"], processed_df["visit"], check_names=False)
    pd.testing.assert_series_equal(
        result["conversion"], processed_df["conversion"], check_names=False
    )
    pd.testing.assert_series_equal(result["spend"], processed_df["spend"], check_names=False)


def test_build_feature_matrix_preserves_customer_id_and_row_count() -> None:
    """
    Encoded features should preserve customer_id and number of rows.
    """
    processed_df = make_sample_processed_df()
    base_df = build_modeling_base_dataset(processed_df)

    encoded_df = build_feature_matrix(base_df)

    assert "customer_id" in encoded_df.columns
    assert len(encoded_df) == len(base_df)
    pd.testing.assert_series_equal(
        encoded_df["customer_id"], base_df["customer_id"], check_names=False
    )


def test_build_feature_matrix_contains_numeric_feature_columns() -> None:
    """
    Numeric feature columns should remain present after encoding.
    """
    processed_df = make_sample_processed_df()
    base_df = build_modeling_base_dataset(processed_df)

    encoded_df = build_feature_matrix(base_df)

    for column in NUMERIC_FEATURE_COLUMNS:
        assert column in encoded_df.columns


def test_build_feature_matrix_creates_expected_dummy_columns() -> None:
    """
    One-hot encoding should create dummy columns for categorical features.
    """
    processed_df = make_sample_processed_df()
    base_df = build_modeling_base_dataset(processed_df)

    encoded_df = build_feature_matrix(base_df)

    expected_dummy_columns = [
        "history_segment_1) $0 - $100",
        "history_segment_2) $100 - $200",
        "history_segment_3) $200 - $350",
        "zip_code_Rural",
        "zip_code_Suburban",
        "zip_code_Urban",
        "channel_Multichannel",
        "channel_Phone",
        "channel_Web",
        "campaign_type_control",
        "campaign_type_mens_email",
        "campaign_type_womens_email",
    ]

    for column in expected_dummy_columns:
        assert column in encoded_df.columns


def test_build_target_dataframe_returns_customer_id_and_requested_target() -> None:
    """
    Target DataFrames should contain only customer_id and the selected target.
    """
    processed_df = make_sample_processed_df()
    base_df = build_modeling_base_dataset(processed_df)

    conversion_target_df = build_target_dataframe(base_df, "conversion")
    visit_target_df = build_target_dataframe(base_df, "visit")
    spend_target_df = build_target_dataframe(base_df, "spend")

    assert list(conversion_target_df.columns) == ["customer_id", "conversion"]
    assert list(visit_target_df.columns) == ["customer_id", "visit"]
    assert list(spend_target_df.columns) == ["customer_id", "spend"]

    assert len(conversion_target_df) == len(base_df)
    assert len(visit_target_df) == len(base_df)
    assert len(spend_target_df) == len(base_df)


def test_build_target_dataframe_preserves_values() -> None:
    """
    Target DataFrames should preserve the original target values exactly.
    """
    processed_df = make_sample_processed_df()
    base_df = build_modeling_base_dataset(processed_df)

    target_df = build_target_dataframe(base_df, "conversion")

    pd.testing.assert_series_equal(
        target_df["conversion"], base_df["conversion"], check_names=False
    )


def test_build_feature_summary_matches_input_shapes_and_target_stats() -> None:
    """
    Feature summary should correctly describe the modeling datasets.
    """
    processed_df = make_sample_processed_df()
    base_df = build_modeling_base_dataset(processed_df)
    encoded_df = build_feature_matrix(base_df)

    summary_df = build_feature_summary(base_df=base_df, encoded_df=encoded_df)

    assert len(summary_df) == 1
    assert summary_df.loc[0, "n_rows"] == len(base_df)
    assert summary_df.loc[0, "n_base_columns"] == base_df.shape[1]
    assert summary_df.loc[0, "n_encoded_feature_columns"] == encoded_df.shape[1]
    assert summary_df.loc[0, "n_numeric_features"] == len(NUMERIC_FEATURE_COLUMNS)
    assert summary_df.loc[0, "n_categorical_features"] == len(CATEGORICAL_FEATURE_COLUMNS)
    assert summary_df.loc[0, "target_visit_rate"] == base_df["visit"].mean()
    assert summary_df.loc[0, "target_conversion_rate"] == base_df["conversion"].mean()
    assert summary_df.loc[0, "target_average_spend"] == base_df["spend"].mean()