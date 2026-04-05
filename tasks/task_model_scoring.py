"""
Pytask task for baseline model scoring in the conversion uplift project.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Annotated

from pytask import Product

from conversion_uplift.config import (
    BLD_CHARTS_DIR,
    BLD_DATA_FINAL_DIR,
    BLD_REPORTS_DIR,
    CHARTS_DIR,
    FINAL_DATA_DIR,
    REPORTS_DIR,
    create_build_directories,
)
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


FEATURES_FILE = FINAL_DATA_DIR / "modeling_features_encoded.csv"
TARGET_CONVERSION_FILE = FINAL_DATA_DIR / "modeling_target_conversion.csv"
TARGET_VISIT_FILE = FINAL_DATA_DIR / "modeling_target_visit.csv"
TARGET_SPEND_FILE = FINAL_DATA_DIR / "modeling_target_spend.csv"

CONVERSION_METRICS_FILE = REPORTS_DIR / "modeling_classification_conversion_metrics.csv"
VISIT_METRICS_FILE = REPORTS_DIR / "modeling_classification_visit_metrics.csv"
SPEND_METRICS_FILE = REPORTS_DIR / "modeling_regression_spend_metrics.csv"

CONVERSION_PR_AUC_CHART = CHARTS_DIR / "conversion_model_pr_auc_comparison.png"
VISIT_PR_AUC_CHART = CHARTS_DIR / "visit_model_pr_auc_comparison.png"
SPEND_RMSE_CHART = CHARTS_DIR / "spend_model_rmse_comparison.png"

BLD_FEATURES_FILE = BLD_DATA_FINAL_DIR / "modeling_features_encoded.csv"
BLD_TARGET_CONVERSION_FILE = BLD_DATA_FINAL_DIR / "modeling_target_conversion.csv"
BLD_TARGET_VISIT_FILE = BLD_DATA_FINAL_DIR / "modeling_target_visit.csv"
BLD_TARGET_SPEND_FILE = BLD_DATA_FINAL_DIR / "modeling_target_spend.csv"

BLD_CONVERSION_METRICS_FILE = (
    BLD_REPORTS_DIR / "modeling_classification_conversion_metrics.csv"
)
BLD_VISIT_METRICS_FILE = BLD_REPORTS_DIR / "modeling_classification_visit_metrics.csv"
BLD_SPEND_METRICS_FILE = BLD_REPORTS_DIR / "modeling_regression_spend_metrics.csv"

BLD_CONVERSION_PR_AUC_CHART = BLD_CHARTS_DIR / "conversion_model_pr_auc_comparison.png"
BLD_VISIT_PR_AUC_CHART = BLD_CHARTS_DIR / "visit_model_pr_auc_comparison.png"
BLD_SPEND_RMSE_CHART = BLD_CHARTS_DIR / "spend_model_rmse_comparison.png"


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

    The task writes the canonical tracked outputs to `outputs/reports/` and
    `outputs/charts/`, and also writes mirrored build copies into `bld/`.
    """
    create_build_directories()
    create_output_directories()
    apply_chart_style()

    features_path = depends_on_features if depends_on_features.exists() else BLD_FEATURES_FILE
    conversion_path = (
        depends_on_conversion if depends_on_conversion.exists() else BLD_TARGET_CONVERSION_FILE
    )
    visit_path = depends_on_visit if depends_on_visit.exists() else BLD_TARGET_VISIT_FILE
    spend_path = depends_on_spend if depends_on_spend.exists() else BLD_TARGET_SPEND_FILE

    features_df = load_csv(features_path)
    conversion_df = load_csv(conversion_path)
    visit_df = load_csv(visit_path)
    spend_df = load_csv(spend_path)

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

    save_dataframe(conversion_results, BLD_CONVERSION_METRICS_FILE)
    save_dataframe(visit_results, BLD_VISIT_METRICS_FILE)
    save_dataframe(spend_results, BLD_SPEND_METRICS_FILE)

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

    shutil.copy2(produces_conversion_chart, BLD_CONVERSION_PR_AUC_CHART)
    shutil.copy2(produces_visit_chart, BLD_VISIT_PR_AUC_CHART)
    shutil.copy2(produces_spend_chart, BLD_SPEND_RMSE_CHART)