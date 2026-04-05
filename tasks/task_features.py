"""
Pytask task for feature preparation in the conversion uplift project.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import pandas as pd
from pytask import Product

from conversion_uplift.features import (
    build_feature_matrix,
    build_feature_summary,
    build_modeling_base_dataset,
    build_target_dataframe,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DATA_FILE = PROJECT_ROOT / "data" / "processed" / "hillstrom_processed.csv"

MODELING_BASE_FILE = PROJECT_ROOT / "data" / "final" / "modeling_base_dataset.csv"
MODELING_FEATURES_FILE = PROJECT_ROOT / "data" / "final" / "modeling_features_encoded.csv"
MODELING_TARGET_VISIT_FILE = PROJECT_ROOT / "data" / "final" / "modeling_target_visit.csv"
MODELING_TARGET_CONVERSION_FILE = (
    PROJECT_ROOT / "data" / "final" / "modeling_target_conversion.csv"
)
MODELING_TARGET_SPEND_FILE = PROJECT_ROOT / "data" / "final" / "modeling_target_spend.csv"

FEATURE_SUMMARY_FILE = PROJECT_ROOT / "outputs" / "reports" / "feature_dataset_summary.csv"


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
    """
    processed_df = pd.read_csv(depends_on)

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