"""
Pytask task for uplift modeling in the conversion uplift project.
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
from conversion_uplift.uplift import (
    apply_chart_style,
    build_segment_uplift_summary,
    build_uplift_decile_summary,
    create_output_directories,
    load_csv,
    plot_observed_uplift_by_decile,
    plot_uplift_by_decile,
    plot_uplift_score_distribution,
    prepare_uplift_dataset,
    save_dataframe,
    train_two_model_uplift,
)


FEATURES_FILE = FINAL_DATA_DIR / "modeling_features_encoded.csv"
BASE_DATASET_FILE = FINAL_DATA_DIR / "modeling_base_dataset.csv"
TARGET_CONVERSION_FILE = FINAL_DATA_DIR / "modeling_target_conversion.csv"

UPLIFT_SCORED_FILE = REPORTS_DIR / "uplift_conversion_scored.csv"
UPLIFT_DECILE_SUMMARY_FILE = REPORTS_DIR / "uplift_conversion_decile_summary.csv"
UPLIFT_SEGMENT_SUMMARY_FILE = REPORTS_DIR / "uplift_segment_summary.csv"

UPLIFT_BY_DECILE_CHART = CHARTS_DIR / "uplift_by_decile.png"
OBSERVED_UPLIFT_BY_DECILE_CHART = CHARTS_DIR / "observed_uplift_by_decile.png"
UPLIFT_SCORE_DISTRIBUTION_CHART = CHARTS_DIR / "uplift_score_distribution.png"

BLD_FEATURES_FILE = BLD_DATA_FINAL_DIR / "modeling_features_encoded.csv"
BLD_BASE_DATASET_FILE = BLD_DATA_FINAL_DIR / "modeling_base_dataset.csv"
BLD_TARGET_CONVERSION_FILE = BLD_DATA_FINAL_DIR / "modeling_target_conversion.csv"

BLD_UPLIFT_SCORED_FILE = BLD_REPORTS_DIR / "uplift_conversion_scored.csv"
BLD_UPLIFT_DECILE_SUMMARY_FILE = BLD_REPORTS_DIR / "uplift_conversion_decile_summary.csv"
BLD_UPLIFT_SEGMENT_SUMMARY_FILE = BLD_REPORTS_DIR / "uplift_segment_summary.csv"

BLD_UPLIFT_BY_DECILE_CHART = BLD_CHARTS_DIR / "uplift_by_decile.png"
BLD_OBSERVED_UPLIFT_BY_DECILE_CHART = BLD_CHARTS_DIR / "observed_uplift_by_decile.png"
BLD_UPLIFT_SCORE_DISTRIBUTION_CHART = BLD_CHARTS_DIR / "uplift_score_distribution.png"


def task_uplift_modeling(
    depends_on_features: Path = FEATURES_FILE,
    depends_on_base_dataset: Path = BASE_DATASET_FILE,
    depends_on_conversion: Path = TARGET_CONVERSION_FILE,
    produces_scored: Annotated[Path, Product] = UPLIFT_SCORED_FILE,
    produces_decile_summary: Annotated[Path, Product] = UPLIFT_DECILE_SUMMARY_FILE,
    produces_segment_summary: Annotated[Path, Product] = UPLIFT_SEGMENT_SUMMARY_FILE,
    produces_uplift_by_decile_chart: Annotated[Path, Product] = UPLIFT_BY_DECILE_CHART,
    produces_observed_uplift_chart: Annotated[Path, Product] = OBSERVED_UPLIFT_BY_DECILE_CHART,
    produces_distribution_chart: Annotated[Path, Product] = UPLIFT_SCORE_DISTRIBUTION_CHART,
) -> None:
    """
    Train the uplift workflow and save customer-level, decile-level,
    and segment-level outputs.

    The task writes the canonical tracked outputs to `outputs/reports/` and
    `outputs/charts/`, and also writes mirrored build copies into `bld/`.
    """
    create_build_directories()
    create_output_directories()
    apply_chart_style()

    features_path = depends_on_features if depends_on_features.exists() else BLD_FEATURES_FILE
    base_dataset_path = (
        depends_on_base_dataset if depends_on_base_dataset.exists() else BLD_BASE_DATASET_FILE
    )
    conversion_path = (
        depends_on_conversion if depends_on_conversion.exists() else BLD_TARGET_CONVERSION_FILE
    )

    features_df = load_csv(features_path)
    base_df = load_csv(base_dataset_path)
    conversion_df = load_csv(conversion_path)

    uplift_df = prepare_uplift_dataset(features_df, base_df, conversion_df)
    scored_df = train_two_model_uplift(uplift_df)
    decile_summary_df = build_uplift_decile_summary(scored_df)
    segment_summary_df = build_segment_uplift_summary(scored_df)

    save_dataframe(scored_df, produces_scored)
    save_dataframe(decile_summary_df, produces_decile_summary)
    save_dataframe(segment_summary_df, produces_segment_summary)

    save_dataframe(scored_df, BLD_UPLIFT_SCORED_FILE)
    save_dataframe(decile_summary_df, BLD_UPLIFT_DECILE_SUMMARY_FILE)
    save_dataframe(segment_summary_df, BLD_UPLIFT_SEGMENT_SUMMARY_FILE)

    plot_uplift_by_decile(decile_summary_df)
    plot_observed_uplift_by_decile(decile_summary_df)
    plot_uplift_score_distribution(scored_df)

    shutil.copy2(produces_uplift_by_decile_chart, BLD_UPLIFT_BY_DECILE_CHART)
    shutil.copy2(produces_observed_uplift_chart, BLD_OBSERVED_UPLIFT_BY_DECILE_CHART)
    shutil.copy2(produces_distribution_chart, BLD_UPLIFT_SCORE_DISTRIBUTION_CHART)