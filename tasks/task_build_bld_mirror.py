"""
Pytask task for rebuilding the ignored bld/ mirror layer in the
conversion uplift project.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Annotated

import pandas as pd
from pytask import Product

from conversion_uplift.config import (
    BLD_CHARTS_DIR,
    BLD_DATA_FINAL_DIR,
    BLD_DATA_PROCESSED_DIR,
    BLD_REPORTS_DIR,
    CHARTS_DIR,
    FINAL_DATA_DIR,
    PROCESSED_DATA_DIR,
    REPORTS_DIR,
    create_build_directories,
)


PROCESSED_SOURCE_FILE = PROCESSED_DATA_DIR / "hillstrom_processed.csv"

FINAL_SOURCE_FILES = [
    FINAL_DATA_DIR / "campaign_summary.csv",
    FINAL_DATA_DIR / "channel_campaign_summary.csv",
    FINAL_DATA_DIR / "customer_experiment_detail.csv",
    FINAL_DATA_DIR / "history_segment_campaign_summary.csv",
    FINAL_DATA_DIR / "modeling_base_dataset.csv",
    FINAL_DATA_DIR / "modeling_features_encoded.csv",
    FINAL_DATA_DIR / "modeling_target_conversion.csv",
    FINAL_DATA_DIR / "modeling_target_spend.csv",
    FINAL_DATA_DIR / "modeling_target_visit.csv",
    FINAL_DATA_DIR / "newbie_campaign_summary.csv",
    FINAL_DATA_DIR / "segment_uplift_summary.csv",
    FINAL_DATA_DIR / "treatment_control_summary.csv",
    FINAL_DATA_DIR / "zip_campaign_summary.csv",
]

CHART_SOURCE_FILES = [
    CHARTS_DIR / "average_spend_by_campaign_type.png",
    CHARTS_DIR / "campaign_outcome_bubble.png",
    CHARTS_DIR / "conversion_model_pr_auc_comparison.png",
    CHARTS_DIR / "conversion_rate_by_campaign_type.png",
    CHARTS_DIR / "history_segment_average_spend_ranked.png",
    CHARTS_DIR / "history_segment_conversion_rate_ranked.png",
    CHARTS_DIR / "observed_uplift_by_decile.png",
    CHARTS_DIR / "segment_outcome_heatmap_normalized.png",
    CHARTS_DIR / "spend_model_rmse_comparison.png",
    CHARTS_DIR / "treatment_control_average_spend_dumbbell.png",
    CHARTS_DIR / "treatment_control_conversion_rate_dumbbell.png",
    CHARTS_DIR / "treatment_control_visit_rate_dumbbell.png",
    CHARTS_DIR / "uplift_by_decile.png",
    CHARTS_DIR / "uplift_score_distribution.png",
    CHARTS_DIR / "visit_model_pr_auc_comparison.png",
    CHARTS_DIR / "visit_rate_by_campaign_type.png",
]

REPORT_SOURCE_FILES = [
    REPORTS_DIR / "feature_dataset_summary.csv",
    REPORTS_DIR / "modeling_classification_conversion_metrics.csv",
    REPORTS_DIR / "modeling_classification_visit_metrics.csv",
    REPORTS_DIR / "modeling_regression_spend_metrics.csv",
    REPORTS_DIR / "mysql_load_summary.csv",
    REPORTS_DIR / "python_campaign_type_summary.csv",
    REPORTS_DIR / "python_outcome_overview.csv",
    REPORTS_DIR / "python_segment_summary.csv",
    REPORTS_DIR / "python_treatment_control_summary.csv",
    REPORTS_DIR / "raw_data_ingestion_summary.csv",
    REPORTS_DIR / "reporting_export_summary.csv",
    REPORTS_DIR / "uplift_conversion_decile_summary.csv",
    REPORTS_DIR / "uplift_conversion_scored.csv",
    REPORTS_DIR / "uplift_segment_summary.csv",
]

BLD_MIRROR_STAMP_FILE = BLD_REPORTS_DIR / "bld_mirror_summary.csv"


def _copy_files(files: list[Path], destination_dir: Path) -> list[str]:
    """
    Copy a list of files into a destination directory and return copied names.
    """
    copied_names: list[str] = []

    for source_file in files:
        if source_file.exists():
            shutil.copy2(source_file, destination_dir / source_file.name)
            copied_names.append(source_file.name)

    return copied_names


def task_build_bld_mirror(
    depends_on_processed: Path = PROCESSED_SOURCE_FILE,
    produces: Annotated[Path, Product] = BLD_MIRROR_STAMP_FILE,
) -> None:
    """
    Rebuild the ignored bld/ mirror from tracked portfolio outputs.

    This task exists so that deleting `bld/` and rerunning `pixi run pytask`
    will recreate the reproducibility layer even when tracked outputs in
    `data/` and `outputs/` are already up to date.
    """
    _ = depends_on_processed

    create_build_directories()

    processed_copied = []
    if PROCESSED_SOURCE_FILE.exists():
        shutil.copy2(
            PROCESSED_SOURCE_FILE,
            BLD_DATA_PROCESSED_DIR / PROCESSED_SOURCE_FILE.name,
        )
        processed_copied.append(PROCESSED_SOURCE_FILE.name)

    final_copied = _copy_files(FINAL_SOURCE_FILES, BLD_DATA_FINAL_DIR)
    charts_copied = _copy_files(CHART_SOURCE_FILES, BLD_CHARTS_DIR)
    reports_copied = _copy_files(REPORT_SOURCE_FILES, BLD_REPORTS_DIR)

    summary_df = pd.DataFrame(
        {
            "processed_files_copied": [len(processed_copied)],
            "final_files_copied": [len(final_copied)],
            "chart_files_copied": [len(charts_copied)],
            "report_files_copied": [len(reports_copied)],
            "processed_file_names": [", ".join(processed_copied)],
            "final_file_names": [", ".join(final_copied)],
            "chart_file_names": [", ".join(charts_copied)],
            "report_file_names": [", ".join(reports_copied)],
        }
    )

    produces.parent.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(produces, index=False)