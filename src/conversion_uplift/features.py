"""
Feature preparation utilities for the conversion uplift project.

This module prepares modeling-ready datasets from the processed Hillstrom data.
It creates:
- a reusable modeling base dataset
- one-hot encoded feature matrix
- separate target files for visit, conversion, and spend

Main responsibilities:
- Load processed data
- Define modeling columns
- One-hot encode categorical features
- Separate feature matrix and targets
- Save modeling-ready datasets for later use
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DATA_FILE = PROJECT_ROOT / "data" / "processed" / "hillstrom_processed.csv"

FINAL_DATA_DIR = PROJECT_ROOT / "data" / "final"
OUTPUTS_REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports"

TARGET_COLUMNS = ["visit", "conversion", "spend"]

NUMERIC_FEATURE_COLUMNS = [
    "recency",
    "history",
    "mens",
    "womens",
    "newbie",
    "binary_treatment_flag",
]

CATEGORICAL_FEATURE_COLUMNS = [
    "history_segment",
    "zip_code",
    "channel",
    "campaign_type",
]

IDENTIFIER_COLUMNS = [
    "customer_id",
    "segment",
]


def load_processed_data(file_path: Path | None = None) -> pd.DataFrame:
    """
    Load the processed Hillstrom dataset from disk.

    Args:
        file_path: Optional custom file path.

    Returns:
        pd.DataFrame: Processed dataset.

    Raises:
        FileNotFoundError: If the processed dataset does not exist.
    """
    path = file_path if file_path is not None else PROCESSED_DATA_FILE

    if not path.exists():
        raise FileNotFoundError(
            f"Processed data file not found at: {path}\n"
            "Please run the preprocessing pipeline first."
        )

    return pd.read_csv(path)


def create_output_directories() -> None:
    """
    Create final output directories if they do not already exist.
    """
    FINAL_DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def build_modeling_base_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build the base modeling dataset before encoding.

    This dataset keeps identifiers, raw feature columns, and target columns
    together so the project has one transparent modeling source table.

    Args:
        df: Processed dataset.

    Returns:
        pd.DataFrame: Base modeling dataset.
    """
    selected_columns = (
        IDENTIFIER_COLUMNS
        + NUMERIC_FEATURE_COLUMNS
        + CATEGORICAL_FEATURE_COLUMNS
        + TARGET_COLUMNS
    )

    return df[selected_columns].copy()


def build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build the one-hot encoded feature matrix for modeling.

    Args:
        df: Base modeling dataset.

    Returns:
        pd.DataFrame: Encoded feature matrix including customer_id.
    """
    feature_columns = (
        ["customer_id"] + NUMERIC_FEATURE_COLUMNS + CATEGORICAL_FEATURE_COLUMNS
    )

    features = df[feature_columns].copy()

    encoded_features = pd.get_dummies(
        features,
        columns=CATEGORICAL_FEATURE_COLUMNS,
        drop_first=False,
        dtype=int,
    )

    return encoded_features


def build_target_dataframe(
    df: pd.DataFrame,
    target_column: str,
) -> pd.DataFrame:
    """
    Build a target dataset for one specific modeling outcome.

    Args:
        df: Base modeling dataset.
        target_column: Name of the target column.

    Returns:
        pd.DataFrame: Target dataset with customer_id and target value.
    """
    return df[["customer_id", target_column]].copy()


def build_feature_summary(
    base_df: pd.DataFrame,
    encoded_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build a small summary table describing the modeling datasets.

    Args:
        base_df: Base modeling dataset.
        encoded_df: Encoded feature matrix.

    Returns:
        pd.DataFrame: One-row summary of modeling data structure.
    """
    summary = pd.DataFrame(
        {
            "n_rows": [len(base_df)],
            "n_base_columns": [base_df.shape[1]],
            "n_encoded_feature_columns": [encoded_df.shape[1]],
            "n_numeric_features": [len(NUMERIC_FEATURE_COLUMNS)],
            "n_categorical_features": [len(CATEGORICAL_FEATURE_COLUMNS)],
            "target_visit_rate": [base_df["visit"].mean()],
            "target_conversion_rate": [base_df["conversion"].mean()],
            "target_average_spend": [base_df["spend"].mean()],
        }
    )

    return summary


def save_dataframe(df: pd.DataFrame, output_path: Path) -> Path:
    """
    Save a DataFrame to CSV.

    Args:
        df: DataFrame to save.
        output_path: Full output path.

    Returns:
        Path: Saved file path.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return output_path


def summarize_feature_outputs(saved_paths: list[Path]) -> None:
    """
    Print a summary of saved feature-preparation outputs.

    Args:
        saved_paths: List of saved file paths.
    """
    print("Feature preparation completed successfully.")
    print("\nSaved files:")

    for path in saved_paths:
        print(f"- {path}")


def main() -> None:
    """
    Run the feature-preparation pipeline.
    """
    create_output_directories()

    processed_df = load_processed_data()
    modeling_base_df = build_modeling_base_dataset(processed_df)
    encoded_features_df = build_feature_matrix(modeling_base_df)

    target_visit_df = build_target_dataframe(modeling_base_df, "visit")
    target_conversion_df = build_target_dataframe(modeling_base_df, "conversion")
    target_spend_df = build_target_dataframe(modeling_base_df, "spend")

    feature_summary_df = build_feature_summary(
        base_df=modeling_base_df,
        encoded_df=encoded_features_df,
    )

    saved_paths = []
    saved_paths.append(
        save_dataframe(
            modeling_base_df,
            FINAL_DATA_DIR / "modeling_base_dataset.csv",
        )
    )
    saved_paths.append(
        save_dataframe(
            encoded_features_df,
            FINAL_DATA_DIR / "modeling_features_encoded.csv",
        )
    )
    saved_paths.append(
        save_dataframe(
            target_visit_df,
            FINAL_DATA_DIR / "modeling_target_visit.csv",
        )
    )
    saved_paths.append(
        save_dataframe(
            target_conversion_df,
            FINAL_DATA_DIR / "modeling_target_conversion.csv",
        )
    )
    saved_paths.append(
        save_dataframe(
            target_spend_df,
            FINAL_DATA_DIR / "modeling_target_spend.csv",
        )
    )
    saved_paths.append(
        save_dataframe(
            feature_summary_df,
            OUTPUTS_REPORTS_DIR / "feature_dataset_summary.csv",
        )
    )

    summarize_feature_outputs(saved_paths)


if __name__ == "__main__":
    main()