"""
Pytask task for feature preparation in the conversion uplift project.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import pandas as pd
from pytask import Product

from conversion_uplift.config import (
    BLD_DATA_FINAL_DIR,
    BLD_DATA_PROCESSED_DIR,
    BLD_REPORTS_DIR,
    FINAL_DATA_DIR,
    PROCESSED_DATA_DIR,
    REPORTS_DIR,
    create_build_directories,
)
from conversion_uplift.features import (
    build_feature_matrix,
    build_feature_summary,
    build_modeling_base_dataset,
    build_target_dataframe,
)


PROCESSED_DATA_FILE = PROCESSED_DATA_DIR / "hillstrom_processed.csv"

MODELING_BASE_FILE = FINAL_DATA_DIR / "modeling_base_dataset.csv"
MODELING_FEATURES_FILE = FINAL_DATA_DIR / "modeling_features_encoded.csv"
MODELING_TARGET_VISIT_FILE = FINAL_DATA_DIR / "modeling_target_visit.csv"
MODELING_TARGET_CONVERSION_FILE = FINAL_DATA_DIR / "modeling_target_conversion.csv"
MODELING_TARGET_SPEND_FILE = FINAL_DATA_DIR / "modeling_target_spend.csv"

FEATURE_SUMMARY_FILE = REPORTS_DIR / "feature_dataset_summary.csv"

BLD_PROCESSED_DATA_FILE = BLD_DATA_PROCESSED_DIR / "hillstrom_processed.csv"
BLD_MODELING_BASE_FILE = BLD_DATA_FINAL_DIR / "modeling_base_dataset.csv"
BLD_MODELING_FEATURES_FILE = BLD_DATA_FINAL_DIR / "modeling_features_encoded.csv"
BLD_MODELING_TARGET_VISIT_FILE = BLD_DATA_FINAL_DIR / "modeling_target_visit.csv"
BLD_MODELING_TARGET_CONVERSION_FILE = BLD_DATA_FINAL_DIR / "modeling_target_conversion.csv"
BLD_MODELING_TARGET_SPEND_FILE = BLD_DATA_FINAL_DIR / "modeling_target_spend.csv"
BLD_FEATURE_SUMMARY_FILE = BLD_REPORTS_DIR / "feature_dataset_summary.csv"


def task_build_features(
    depends_on: Path = PROCESSED_DATA_FILE,
    produces_modeling_base: Annotated[Path, Product] = MODELING_BASE_FILE,
    produces_modeling_features: Annotated[Path, Product] = MODELING_FEATURES_FILE,
    produces_target_visit: Annotated[Path, Product] = MODELING_TARGET_VISIT_FILE,
    produces_target_conversion: Annotated[Path, Product] = MODELING_TARGET_CONVERSION_FILE,
    produces_target_spend: Annotated[Path, Product] = MODELING_TARGET_SPEND_FILE,
    produces_feature_summary: Annotated[Path, Product] = FEATURE_SUMMARY_FILE,
) -> None:
    """
    Build modeling-ready feature and target datasets from the processed data.

    The task writes the canonical tracked outputs to `data/final/` and
    `outputs/reports/`, and also writes mirrored build copies into `bld/`.
    """
    create_build_directories()

    source_path = depends_on if depends_on.exists() else BLD_PROCESSED_DATA_FILE
    processed_df = pd.read_csv(source_path)

    modeling_base_df = build_modeling_base_dataset(processed_df)
    encoded_features_df = build_feature_matrix(modeling_base_df)

    target_visit_df = build_target_dataframe(modeling_base_df, "visit")
    target_conversion_df = build_target_dataframe(modeling_base_df, "conversion")
    target_spend_df = build_target_dataframe(modeling_base_df, "spend")

    feature_summary_df = build_feature_summary(
        base_df=modeling_base_df,
        encoded_df=encoded_features_df,
    )

    produces_modeling_base.parent.mkdir(parents=True, exist_ok=True)
    produces_feature_summary.parent.mkdir(parents=True, exist_ok=True)

    modeling_base_df.to_csv(produces_modeling_base, index=False)
    encoded_features_df.to_csv(produces_modeling_features, index=False)
    target_visit_df.to_csv(produces_target_visit, index=False)
    target_conversion_df.to_csv(produces_target_conversion, index=False)
    target_spend_df.to_csv(produces_target_spend, index=False)
    feature_summary_df.to_csv(produces_feature_summary, index=False)

    modeling_base_df.to_csv(BLD_MODELING_BASE_FILE, index=False)
    encoded_features_df.to_csv(BLD_MODELING_FEATURES_FILE, index=False)
    target_visit_df.to_csv(BLD_MODELING_TARGET_VISIT_FILE, index=False)
    target_conversion_df.to_csv(BLD_MODELING_TARGET_CONVERSION_FILE, index=False)
    target_spend_df.to_csv(BLD_MODELING_TARGET_SPEND_FILE, index=False)
    feature_summary_df.to_csv(BLD_FEATURE_SUMMARY_FILE, index=False)