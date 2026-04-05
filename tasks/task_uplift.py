"""
Pytask task for uplift modeling in the conversion uplift project.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from pytask import Product

from conversion_uplift.uplift import (
    apply_chart_style,
    build_segment_uplift_summary,
    build_uplift_decile_summary,
    create_output_directories,
    load_uplift_inputs,
    plot_observed_uplift_by_decile,
    plot_uplift_by_decile,
    plot_uplift_score_distribution,
    prepare_uplift_dataset,
    save_dataframe,
    train_two_model_uplift,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

FEATURES_FILE = PROJECT_ROOT / "data" / "final" / "modeling_features_encoded.csv"
BASE_DATASET_FILE = PROJECT_ROOT / "data" / "final" / "modeling_base_dataset.csv"
TARGET_CONVERSION_FILE = PROJECT_ROOT / "data" / "final" / "modeling_target_conversion.csv"

UPLIFT_SCORED_FILE = PROJECT_ROOT / "outputs" / "reports" / "uplift_conversion_scored.csv"
UPLIFT_DECILE_SUMMARY_FILE = (
    PROJECT_ROOT / "outputs" / "reports" / "uplift_conversion_decile_summary.csv"
)
UPLIFT_SEGMENT_SUMMARY_FILE = (
    PROJECT_ROOT / "outputs" / "reports" / "uplift_segment_summary.csv"
)

UPLIFT_BY_DECILE_CHART = PROJECT_ROOT / "outputs" / "charts" / "uplift_by_decile.png"
OBSERVED_UPLIFT_BY_DECILE_CHART = (
    PROJECT_ROOT / "outputs" / "charts" / "observed_uplift_by_decile.png"
)
UPLIFT_SCORE_DISTRIBUTION_CHART = (
    PROJECT_ROOT / "outputs" / "charts" / "uplift_score_distribution.png"
)


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
    """
    create_output_directories()
    apply_chart_style()

    # Reuse the same loading function from uplift.py, but make sure
    # pytask sees the explicit file dependencies above.
    _ = depends_on_features, depends_on_base_dataset, depends_on_conversion
    features_df, base_df, conversion_df = load_uplift_inputs()

    uplift_df = prepare_uplift_dataset(features_df, base_df, conversion_df)
    scored_df = train_two_model_uplift(uplift_df)
    decile_summary_df = build_uplift_decile_summary(scored_df)
    segment_summary_df = build_segment_uplift_summary(scored_df)

    save_dataframe(scored_df, produces_scored)
    save_dataframe(decile_summary_df, produces_decile_summary)
    save_dataframe(segment_summary_df, produces_segment_summary)

    plot_uplift_by_decile(decile_summary_df)
    plot_observed_uplift_by_decile(decile_summary_df)
    plot_uplift_score_distribution(scored_df)