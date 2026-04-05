"""
Lightweight integration-style tests for the preprocessing -> features pipeline.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from conversion_uplift.features import (
    build_feature_matrix,
    build_feature_summary,
    build_modeling_base_dataset,
    build_target_dataframe,
)
from conversion_uplift.preprocess import preprocess_data, save_processed_data


def make_raw_input_df() -> pd.DataFrame:
    """
    Build a small raw dataset that can flow through preprocessing and feature prep.
    """
    return pd.DataFrame(
        {
            "recency": [1, 2, 3, 4, 5, 6],
            "history_segment": [
                "1) $0 - $100",
                "2) $100 - $200",
                "3) $200 - $350",
                "4) $350 - $500",
                "5) $500 - $750",
                "6) $750 - $1,000",
            ],
            "history": [42.0, 110.5, 220.0, 340.0, 520.0, 810.0],
            "mens": [1, 0, 1, 0, 1, 0],
            "womens": [0, 1, 0, 1, 0, 1],
            "zip_code": ["Urban", "Suburban", "Rural", "Urban", "Suburban", "Rural"],
            "newbie": [1, 0, 1, 0, 1, 0],
            "channel": ["Web", "Phone", "Multichannel", "Web", "Phone", "Multichannel"],
            "segment": [
                "Mens E-Mail",
                "No E-Mail",
                "Womens E-Mail",
                "No E-Mail",
                "Mens E-Mail",
                "Womens E-Mail",
            ],
            "visit": [1, 0, 1, 0, 1, 1],
            "conversion": [0, 0, 1, 0, 1, 0],
            "spend": [0.0, 0.0, 25.0, 0.0, 40.0, 10.0],
        }
    )


def test_preprocess_to_features_pipeline(monkeypatch, tmp_path: Path) -> None:
    """
    A small raw dataset should pass through preprocessing and feature generation
    with consistent row counts and aligned targets.
    """
    raw_df = make_raw_input_df()

    monkeypatch.setattr(
        "conversion_uplift.preprocess.load_raw_data",
        lambda: raw_df.copy(),
    )

    processed_df = preprocess_data()
    output_path = tmp_path / "hillstrom_processed.csv"
    saved_path = save_processed_data(processed_df, output_path=output_path)

    assert saved_path.exists()
    assert len(processed_df) == len(raw_df)
    assert "customer_id" in processed_df.columns
    assert "binary_treatment_flag" in processed_df.columns
    assert "campaign_type" in processed_df.columns

    modeling_base_df = build_modeling_base_dataset(processed_df)
    encoded_features_df = build_feature_matrix(modeling_base_df)

    visit_target_df = build_target_dataframe(modeling_base_df, "visit")
    conversion_target_df = build_target_dataframe(modeling_base_df, "conversion")
    spend_target_df = build_target_dataframe(modeling_base_df, "spend")

    feature_summary_df = build_feature_summary(
        base_df=modeling_base_df,
        encoded_df=encoded_features_df,
    )

    assert len(modeling_base_df) == len(processed_df)
    assert len(encoded_features_df) == len(processed_df)
    assert len(visit_target_df) == len(processed_df)
    assert len(conversion_target_df) == len(processed_df)
    assert len(spend_target_df) == len(processed_df)

    pd.testing.assert_series_equal(
        visit_target_df["visit"],
        modeling_base_df["visit"],
        check_names=False,
    )
    pd.testing.assert_series_equal(
        conversion_target_df["conversion"],
        modeling_base_df["conversion"],
        check_names=False,
    )
    pd.testing.assert_series_equal(
        spend_target_df["spend"],
        modeling_base_df["spend"],
        check_names=False,
    )

    assert feature_summary_df.loc[0, "n_rows"] == len(processed_df)
    assert feature_summary_df.loc[0, "target_visit_rate"] == modeling_base_df["visit"].mean()
    assert (
        feature_summary_df.loc[0, "target_conversion_rate"]
        == modeling_base_df["conversion"].mean()
    )
    assert (
        feature_summary_df.loc[0, "target_average_spend"]
        == modeling_base_df["spend"].mean()
    )