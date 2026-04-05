"""
Tests for uplift modeling utilities in the conversion uplift project.
"""

from __future__ import annotations

import pandas as pd

from conversion_uplift.uplift import (
    add_uplift_deciles,
    build_segment_uplift_summary,
    build_uplift_decile_summary,
    get_feature_columns,
    prepare_uplift_dataset,
    train_two_model_uplift,
)


def make_sample_features_df() -> pd.DataFrame:
    """
    Build a small encoded feature dataset for uplift testing.
    """
    return pd.DataFrame(
        {
            "customer_id": list(range(1, 21)),
            "recency": list(range(1, 21)),
            "history": [
                50, 60, 70, 80, 90,
                100, 110, 120, 130, 140,
                150, 160, 170, 180, 190,
                200, 210, 220, 230, 240,
            ],
            "mens": [1, 0] * 10,
            "womens": [0, 1] * 10,
            "newbie": [1, 1, 0, 0, 1] * 4,
            "binary_treatment_flag": [1, 0] * 10,
            "history_segment_1": [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "history_segment_2": [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "history_segment_3": [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "history_segment_4": [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "history_segment_5": [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "history_segment_6": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            "history_segment_7": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
            "zip_code_Urban": [1, 0] * 10,
            "zip_code_Suburban": [0, 1] * 10,
            "channel_Web": [1, 0] * 10,
            "channel_Phone": [0, 1] * 10,
            "campaign_type_control": [0, 1] * 10,
            "campaign_type_email": [1, 0] * 10,
        }
    )


def make_sample_base_df() -> pd.DataFrame:
    """
    Build a small base modeling dataset for uplift testing.
    """
    return pd.DataFrame(
        {
            "customer_id": list(range(1, 21)),
            "segment": [
                "Mens E-Mail", "No E-Mail",
                "Mens E-Mail", "No E-Mail",
                "Womens E-Mail", "No E-Mail",
                "Mens E-Mail", "No E-Mail",
                "Womens E-Mail", "No E-Mail",
                "Mens E-Mail", "No E-Mail",
                "Womens E-Mail", "No E-Mail",
                "Mens E-Mail", "No E-Mail",
                "Womens E-Mail", "No E-Mail",
                "Mens E-Mail", "No E-Mail",
            ],
            "campaign_type": [
                "mens_email", "control",
                "mens_email", "control",
                "womens_email", "control",
                "mens_email", "control",
                "womens_email", "control",
                "mens_email", "control",
                "womens_email", "control",
                "mens_email", "control",
                "womens_email", "control",
                "mens_email", "control",
            ],
            "history_segment": [
                "1) $0 - $100", "1) $0 - $100",
                "2) $100 - $200", "2) $100 - $200",
                "3) $200 - $350", "3) $200 - $350",
                "4) $350 - $500", "4) $350 - $500",
                "5) $500 - $750", "5) $500 - $750",
                "6) $750 - $1,000", "6) $750 - $1,000",
                "7) $1,000 +", "7) $1,000 +",
                "7) $1,000 +", "7) $1,000 +",
                "7) $1,000 +", "7) $1,000 +",
                "7) $1,000 +", "7) $1,000 +",
            ],
            "zip_code": [
                "Urban", "Suburban",
                "Urban", "Suburban",
                "Urban", "Suburban",
                "Urban", "Suburban",
                "Urban", "Suburban",
                "Urban", "Suburban",
                "Urban", "Suburban",
                "Urban", "Suburban",
                "Urban", "Suburban",
                "Urban", "Suburban",
            ],
            "channel": [
                "Web", "Phone",
                "Web", "Phone",
                "Web", "Phone",
                "Web", "Phone",
                "Web", "Phone",
                "Web", "Phone",
                "Web", "Phone",
                "Web", "Phone",
                "Web", "Phone",
                "Web", "Phone",
            ],
            "binary_treatment_flag": [1, 0] * 10,
        }
    )


def make_sample_conversion_df() -> pd.DataFrame:
    """
    Build a conversion target dataset where both treatment and control
    groups contain both classes.
    """
    return pd.DataFrame(
        {
            "customer_id": list(range(1, 21)),
            "conversion": [
                1, 0,
                0, 1,
                1, 0,
                0, 1,
                1, 0,
                0, 1,
                1, 0,
                0, 1,
                1, 0,
                0, 1,
            ],
        }
    )


def test_prepare_uplift_dataset_contains_expected_columns() -> None:
    """
    The uplift dataset should merge encoded features, target, and reporting columns.
    """
    features_df = make_sample_features_df()
    base_df = make_sample_base_df()
    conversion_df = make_sample_conversion_df()

    result = prepare_uplift_dataset(features_df, base_df, conversion_df)

    expected_columns = {
        "customer_id",
        "conversion",
        "segment",
        "campaign_type",
        "history_segment",
        "zip_code",
        "channel",
        "binary_treatment_flag",
    }

    assert expected_columns.issubset(result.columns)
    assert len(result) == len(features_df)


def test_get_feature_columns_excludes_reporting_and_target_columns() -> None:
    """
    Uplift feature columns should exclude identifiers, target, and reporting columns.
    """
    features_df = make_sample_features_df()
    base_df = make_sample_base_df()
    conversion_df = make_sample_conversion_df()
    uplift_df = prepare_uplift_dataset(features_df, base_df, conversion_df)

    feature_columns = get_feature_columns(uplift_df)

    excluded = {
        "customer_id",
        "conversion",
        "segment",
        "campaign_type",
        "history_segment",
        "zip_code",
        "channel",
    }

    assert excluded.isdisjoint(feature_columns)
    assert "binary_treatment_flag" in feature_columns


def test_train_two_model_uplift_returns_expected_columns() -> None:
    """
    The customer-level scored uplift output should contain the main uplift fields.
    """
    features_df = make_sample_features_df()
    base_df = make_sample_base_df()
    conversion_df = make_sample_conversion_df()
    uplift_df = prepare_uplift_dataset(features_df, base_df, conversion_df)

    scored_df = train_two_model_uplift(uplift_df)

    expected_columns = {
        "customer_id",
        "segment",
        "campaign_type",
        "history_segment",
        "zip_code",
        "channel",
        "binary_treatment_flag",
        "conversion",
        "pred_conversion_if_treated",
        "pred_conversion_if_control",
        "uplift_score",
    }

    assert expected_columns.issubset(scored_df.columns)
    assert len(scored_df) == len(uplift_df)


def test_train_two_model_uplift_sorts_by_uplift_score_descending() -> None:
    """
    Customer-level uplift scores should be sorted from highest to lowest.
    """
    features_df = make_sample_features_df()
    base_df = make_sample_base_df()
    conversion_df = make_sample_conversion_df()
    uplift_df = prepare_uplift_dataset(features_df, base_df, conversion_df)

    scored_df = train_two_model_uplift(uplift_df)

    assert scored_df["uplift_score"].is_monotonic_decreasing


def test_add_uplift_deciles_creates_decile_column() -> None:
    """
    Decile assignment should add a non-null uplift_decile column.
    """
    features_df = make_sample_features_df()
    base_df = make_sample_base_df()
    conversion_df = make_sample_conversion_df()
    uplift_df = prepare_uplift_dataset(features_df, base_df, conversion_df)
    scored_df = train_two_model_uplift(uplift_df)

    decile_df = add_uplift_deciles(scored_df)

    assert "uplift_decile" in decile_df.columns
    assert decile_df["uplift_decile"].notna().all()


def test_build_uplift_decile_summary_returns_expected_columns() -> None:
    """
    Decile summary should include predicted and observed uplift validation columns.
    """
    features_df = make_sample_features_df()
    base_df = make_sample_base_df()
    conversion_df = make_sample_conversion_df()
    uplift_df = prepare_uplift_dataset(features_df, base_df, conversion_df)
    scored_df = train_two_model_uplift(uplift_df)

    summary_df = build_uplift_decile_summary(scored_df)

    expected_columns = {
        "uplift_decile",
        "customers",
        "avg_uplift_score",
        "avg_pred_treated",
        "avg_pred_control",
        "observed_conversion_rate",
        "treated_customers",
        "control_customers",
        "treated_conversion_rate",
        "control_conversion_rate",
        "observed_uplift",
    }

    assert expected_columns.issubset(summary_df.columns)
    assert len(summary_df) > 0


def test_build_uplift_decile_summary_customer_counts_match() -> None:
    """
    For each decile, treated + control customers should equal total customers.
    """
    features_df = make_sample_features_df()
    base_df = make_sample_base_df()
    conversion_df = make_sample_conversion_df()
    uplift_df = prepare_uplift_dataset(features_df, base_df, conversion_df)
    scored_df = train_two_model_uplift(uplift_df)

    summary_df = build_uplift_decile_summary(scored_df)

    assert (summary_df["treated_customers"] + summary_df["control_customers"]).equals(
        summary_df["customers"]
    )


def test_build_uplift_decile_summary_observed_uplift_formula_holds() -> None:
    """
    Observed uplift should equal treated conversion rate minus control conversion rate.
    """
    features_df = make_sample_features_df()
    base_df = make_sample_base_df()
    conversion_df = make_sample_conversion_df()
    uplift_df = prepare_uplift_dataset(features_df, base_df, conversion_df)
    scored_df = train_two_model_uplift(uplift_df)

    summary_df = build_uplift_decile_summary(scored_df)

    expected = (
        summary_df["treated_conversion_rate"] - summary_df["control_conversion_rate"]
    )
    pd.testing.assert_series_equal(
        summary_df["observed_uplift"],
        expected,
        check_names=False,
    )


def test_build_segment_uplift_summary_returns_expected_columns() -> None:
    """
    Segment summary should include predicted and observed uplift validation columns.
    """
    features_df = make_sample_features_df()
    base_df = make_sample_base_df()
    conversion_df = make_sample_conversion_df()
    uplift_df = prepare_uplift_dataset(features_df, base_df, conversion_df)
    scored_df = train_two_model_uplift(uplift_df)

    segment_summary_df = build_segment_uplift_summary(scored_df)

    expected_columns = {
        "segment_type",
        "segment_value",
        "customers",
        "avg_uplift_score",
        "avg_pred_treated",
        "avg_pred_control",
        "observed_conversion_rate",
        "treated_customers",
        "control_customers",
        "treated_conversion_rate",
        "control_conversion_rate",
        "observed_uplift",
    }

    assert expected_columns.issubset(segment_summary_df.columns)
    assert len(segment_summary_df) > 0


def test_build_segment_uplift_summary_observed_uplift_formula_holds() -> None:
    """
    Segment-level observed uplift should equal treated minus control conversion rate.
    """
    features_df = make_sample_features_df()
    base_df = make_sample_base_df()
    conversion_df = make_sample_conversion_df()
    uplift_df = prepare_uplift_dataset(features_df, base_df, conversion_df)
    scored_df = train_two_model_uplift(uplift_df)

    segment_summary_df = build_segment_uplift_summary(scored_df)

    expected = (
        segment_summary_df["treated_conversion_rate"]
        - segment_summary_df["control_conversion_rate"]
    )
    pd.testing.assert_series_equal(
        segment_summary_df["observed_uplift"],
        expected,
        check_names=False,
    )