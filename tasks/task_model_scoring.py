"""
Pytask task for baseline model scoring in the conversion uplift project.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from pytask import Product

from conversion_uplift.modeling import (
    apply_chart_style,
    create_output_directories,
    evaluate_classification_models,
    evaluate_regression_models,
    load_csv,
    plot_classification_metric_comparison,
    plot_regression_metric_comparison,
    prepare_feature_matrix,
    prepare_target_series,
    save_dataframe,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

FEATURES_FILE = PROJECT_ROOT / "data" / "final" / "modeling_features_encoded.csv"
TARGET_CONVERSION_FILE = PROJECT_ROOT / "data" / "final" / "modeling_target_conversion.csv"
TARGET_VISIT_FILE = PROJECT_ROOT / "data" / "final" / "modeling_target_visit.csv"
TARGET_SPEND_FILE = PROJECT_ROOT / "data" / "final" / "modeling_target_spend.csv"

CONVERSION_METRICS_FILE = (
    PROJECT_ROOT / "outputs" / "reports" / "modeling_classification_conversion_metrics.csv"
)
VISIT_METRICS_FILE = (
    PROJECT_ROOT / "outputs" / "reports" / "modeling_classification_visit_metrics.csv"
)
SPEND_METRICS_FILE = (
    PROJECT_ROOT / "outputs" / "reports" / "modeling_regression_spend_metrics.csv"
)

CONVERSION_PR_AUC_CHART = (
    PROJECT_ROOT / "outputs" / "charts" / "conversion_model_pr_auc_comparison.png"
)
VISIT_PR_AUC_CHART = (
    PROJECT_ROOT / "outputs" / "charts" / "visit_model_pr_auc_comparison.png"
)
SPEND_RMSE_CHART = (
    PROJECT_ROOT / "outputs" / "charts" / "spend_model_rmse_comparison.png"
)


def task_model_scoring(
    depends_on_features: Path = FEATURES_FILE,
    depends_on_conversion: Path = TARGET_CONVERSION_FILE,
    depends_on_visit: Path = TARGET_VISIT_FILE,
    depends_on_spend: Path = TARGET_SPEND_FILE,
    produces_conversion_metrics: Annotated[Path, Product] = CONVERSION_METRICS_FILE,
    produces_visit_metrics: Annotated[Path, Product] = VISIT_METRICS_FILE,
    produces_spend_metrics: Annotated[Path, Product] = SPEND_METRICS_FILE,
    produces_conversion_chart: Annotated[Path, Product] = CONVERSION_PR_AUC_CHART,
    produces_visit_chart: Annotated[Path, Product] = VISIT_PR_AUC_CHART,
    produces_spend_chart: Annotated[Path, Product] = SPEND_RMSE_CHART,
) -> None:
    """
    Train and score baseline models from prepared feature datasets.
    """
    create_output_directories()
    apply_chart_style()

    features_df = load_csv(depends_on_features)
    conversion_df = load_csv(depends_on_conversion)
    visit_df = load_csv(depends_on_visit)
    spend_df = load_csv(depends_on_spend)

    X, _ = prepare_feature_matrix(features_df)

    y_conversion = prepare_target_series(conversion_df, "conversion")
    y_visit = prepare_target_series(visit_df, "visit")
    y_spend = prepare_target_series(spend_df, "spend")

    conversion_results = evaluate_classification_models(
        X=X,
        y=y_conversion,
        target_name="conversion",
    )
    visit_results = evaluate_classification_models(
        X=X,
        y=y_visit,
        target_name="visit",
    )
    spend_results = evaluate_regression_models(
        X=X,
        y=y_spend,
        target_name="spend",
    )

    save_dataframe(conversion_results, produces_conversion_metrics)
    save_dataframe(visit_results, produces_visit_metrics)
    save_dataframe(spend_results, produces_spend_metrics)

    plot_classification_metric_comparison(
        results_df=conversion_results,
        metric_column="pr_auc",
        filename=produces_conversion_chart.name,
        title="Conversion Model PR-AUC Comparison",
        fmt="{:.4f}",
    )

    plot_classification_metric_comparison(
        results_df=visit_results,
        metric_column="pr_auc",
        filename=produces_visit_chart.name,
        title="Visit Model PR-AUC Comparison",
        fmt="{:.4f}",
    )

    plot_regression_metric_comparison(
        results_df=spend_results,
        metric_column="rmse",
        filename=produces_spend_chart.name,
        title="Spend Model RMSE Comparison",
        fmt="{:.2f}",
    )