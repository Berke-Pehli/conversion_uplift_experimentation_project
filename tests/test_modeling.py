"""
Tests for baseline modeling utilities in the conversion uplift project.
"""

from __future__ import annotations

import pandas as pd

from conversion_uplift.modeling import (
    evaluate_classification_models,
    evaluate_regression_models,
    prepare_feature_matrix,
    prepare_target_series,
)


def make_sample_features_df() -> pd.DataFrame:
    """
    Build a small encoded feature dataset for testing.
    """
    return pd.DataFrame(
        {
            "customer_id": list(range(1, 13)),
            "recency": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            "history": [50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160],
            "mens": [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            "womens": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
            "newbie": [1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0],
            "binary_treatment_flag": [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            "history_segment_1": [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "history_segment_2": [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            "history_segment_3": [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
            "history_segment_4": [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
            "history_segment_5": [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0],
            "history_segment_6": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            "zip_code_Urban": [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            "zip_code_Suburban": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
            "channel_Web": [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            "channel_Phone": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
            "campaign_type_control": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
            "campaign_type_email": [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
        }
    )


def make_sample_target_df(target_name: str, values: list[int | float]) -> pd.DataFrame:
    """
    Build a target dataframe with customer_id and a selected target column.
    """
    return pd.DataFrame(
        {
            "customer_id": list(range(1, len(values) + 1)),
            target_name: values,
        }
    )


def test_prepare_feature_matrix_removes_customer_id_from_x() -> None:
    """
    The feature matrix should exclude customer_id and preserve row count.
    """
    features_df = make_sample_features_df()

    X, customer_ids = prepare_feature_matrix(features_df)

    assert "customer_id" not in X.columns
    assert len(X) == len(features_df)
    assert list(customer_ids) == list(features_df["customer_id"])


def test_prepare_target_series_returns_requested_column() -> None:
    """
    The target series helper should return the requested target column.
    """
    target_df = make_sample_target_df("conversion", [0, 1, 0, 1])

    y = prepare_target_series(target_df, "conversion")

    assert list(y) == [0, 1, 0, 1]


def test_evaluate_classification_models_returns_expected_columns() -> None:
    """
    Classification evaluation should return the expected metric columns.
    """
    features_df = make_sample_features_df()
    X, _ = prepare_feature_matrix(features_df)

    target_df = make_sample_target_df(
        "conversion",
        [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    )
    y = prepare_target_series(target_df, "conversion")

    results_df = evaluate_classification_models(X=X, y=y, target_name="conversion")

    expected_columns = [
        "target",
        "model_name",
        "accuracy",
        "precision",
        "recall",
        "f1_score",
        "roc_auc",
        "pr_auc",
        "positive_prediction_rate",
        "true_negative",
        "false_positive",
        "false_negative",
        "true_positive",
    ]

    assert list(results_df.columns) == expected_columns
    assert len(results_df) == 3
    assert set(results_df["target"]) == {"conversion"}


def test_evaluate_classification_models_sorts_by_pr_auc_descending() -> None:
    """
    Classification results should be sorted by PR-AUC descending.
    """
    features_df = make_sample_features_df()
    X, _ = prepare_feature_matrix(features_df)

    target_df = make_sample_target_df(
        "visit",
        [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    )
    y = prepare_target_series(target_df, "visit")

    results_df = evaluate_classification_models(X=X, y=y, target_name="visit")

    assert results_df["pr_auc"].is_monotonic_decreasing


def test_evaluate_classification_models_confusion_matrix_counts_sum_to_test_size() -> None:
    """
    Confusion matrix counts should sum to the classification test-set size.
    """
    features_df = make_sample_features_df()
    X, _ = prepare_feature_matrix(features_df)

    target_df = make_sample_target_df(
        "conversion",
        [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    )
    y = prepare_target_series(target_df, "conversion")

    results_df = evaluate_classification_models(X=X, y=y, target_name="conversion")

    for _, row in results_df.iterrows():
        total = (
            row["true_negative"]
            + row["false_positive"]
            + row["false_negative"]
            + row["true_positive"]
        )
        assert total > 0


def test_evaluate_regression_models_returns_expected_columns() -> None:
    """
    Regression evaluation should return the expected metric columns.
    """
    features_df = make_sample_features_df()
    X, _ = prepare_feature_matrix(features_df)

    target_df = make_sample_target_df(
        "spend",
        [0.0, 5.0, 0.0, 8.0, 1.0, 10.0, 2.0, 12.0, 3.0, 15.0, 4.0, 20.0],
    )
    y = prepare_target_series(target_df, "spend")

    results_df = evaluate_regression_models(X=X, y=y, target_name="spend")

    expected_columns = [
        "target",
        "model_name",
        "rmse",
        "mae",
        "r2_score",
    ]

    assert list(results_df.columns) == expected_columns
    assert len(results_df) == 3
    assert set(results_df["target"]) == {"spend"}


def test_evaluate_regression_models_sorts_by_rmse_ascending() -> None:
    """
    Regression results should be sorted by RMSE ascending.
    """
    features_df = make_sample_features_df()
    X, _ = prepare_feature_matrix(features_df)

    target_df = make_sample_target_df(
        "spend",
        [0.0, 5.0, 0.0, 8.0, 1.0, 10.0, 2.0, 12.0, 3.0, 15.0, 4.0, 20.0],
    )
    y = prepare_target_series(target_df, "spend")

    results_df = evaluate_regression_models(X=X, y=y, target_name="spend")

    assert results_df["rmse"].is_monotonic_increasing


def test_regression_metrics_are_non_negative_where_expected() -> None:
    """
    RMSE and MAE should be non-negative for all regression models.
    """
    features_df = make_sample_features_df()
    X, _ = prepare_feature_matrix(features_df)

    target_df = make_sample_target_df(
        "spend",
        [0.0, 5.0, 0.0, 8.0, 1.0, 10.0, 2.0, 12.0, 3.0, 15.0, 4.0, 20.0],
    )
    y = prepare_target_series(target_df, "spend")

    results_df = evaluate_regression_models(X=X, y=y, target_name="spend")

    assert (results_df["rmse"] >= 0).all()
    assert (results_df["mae"] >= 0).all()