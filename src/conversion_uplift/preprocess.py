"""
Data preprocessing utilities for the conversion uplift project.

This module transforms the canonical raw Hillstrom dataset into a cleaner
processed dataset that is ready for SQL loading, analysis, and modeling.

Main responsibilities:
- Load raw data
- Standardize and validate values
- Create binary treatment features for modeling
- Preserve the original experiment segment column for reporting
- Save the processed dataset to the processed data folder
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from conversion_uplift.ingest import load_raw_data, validate_raw_columns


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_DATA_FILE = PROCESSED_DATA_DIR / "hillstrom_processed.csv"

VALID_SEGMENTS = {"Mens E-Mail", "Womens E-Mail", "No E-Mail"}
VALID_CHANNELS = {"Phone", "Web", "Multichannel"}
VALID_ZIP_CODES = {"Urban", "Rural", "Suburban"}


def clean_history_segment(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean whitespace in the history_segment column.

    Args:
        df: Input dataset.

    Returns:
        pd.DataFrame: Dataset with cleaned history_segment values.
    """
    df = df.copy()
    df["history_segment"] = df["history_segment"].astype(str).str.strip()
    return df


def clean_zip_code(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize zip_code values.

    Args:
        df: Input dataset.

    Returns:
        pd.DataFrame: Dataset with standardized zip_code values.
    """
    df = df.copy()

    zip_code_mapping = {
        "Surburban": "Suburban",
        "Sururban": "Suburban",
    }

    df["zip_code"] = df["zip_code"].replace(zip_code_mapping)
    return df


def validate_categorical_values(df: pd.DataFrame) -> None:
    """
    Validate key categorical columns against expected value sets.

    Args:
        df: Input dataset.

    Raises:
        ValueError: If invalid values are found.
    """
    invalid_segments = set(df["segment"].dropna().unique()) - VALID_SEGMENTS
    invalid_channels = set(df["channel"].dropna().unique()) - VALID_CHANNELS
    invalid_zip_codes = set(df["zip_code"].dropna().unique()) - VALID_ZIP_CODES

    if invalid_segments:
        raise ValueError(f"Invalid segment values found: {sorted(invalid_segments)}")

    if invalid_channels:
        raise ValueError(f"Invalid channel values found: {sorted(invalid_channels)}")

    if invalid_zip_codes:
        raise ValueError(f"Invalid zip_code values found: {sorted(invalid_zip_codes)}")


def create_customer_id(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a synthetic customer_id based on row order.

    The Hillstrom dataset does not provide a natural customer primary key in
    this format, so we create one for downstream SQL table design.

    Args:
        df: Input dataset.

    Returns:
        pd.DataFrame: Dataset with customer_id added as the first column.
    """
    df = df.copy()
    df.insert(0, "customer_id", range(1, len(df) + 1))
    return df


def create_binary_treatment_flag(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a binary treatment flag for modeling.

    Logic:
    - 1 if the customer received any email treatment
    - 0 if the customer was in the No E-Mail control group

    Args:
        df: Input dataset.

    Returns:
        pd.DataFrame: Dataset with binary_treatment_flag added.
    """
    df = df.copy()
    df["binary_treatment_flag"] = df["segment"].apply(
        lambda value: 0 if value == "No E-Mail" else 1
    )
    return df


def create_segment_type(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a simplified campaign_type column for reporting.

    Args:
        df: Input dataset.

    Returns:
        pd.DataFrame: Dataset with campaign_type added.
    """
    df = df.copy()

    mapping = {
        "Mens E-Mail": "mens_email",
        "Womens E-Mail": "womens_email",
        "No E-Mail": "control",
    }

    df["campaign_type"] = df["segment"].map(mapping)
    return df


def validate_numeric_columns(df: pd.DataFrame) -> None:
    """
    Validate key numeric columns for basic data quality.

    Args:
        df: Input dataset.

    Raises:
        ValueError: If invalid numeric values are found.
    """
    binary_columns = ["mens", "womens", "newbie", "visit", "conversion"]

    for column in binary_columns:
        unique_values = set(df[column].dropna().unique())
        if not unique_values.issubset({0, 1}):
            raise ValueError(
                f"Column '{column}' contains non-binary values: {sorted(unique_values)}"
            )

    if (df["spend"] < 0).any():
        raise ValueError("Column 'spend' contains negative values.")

    if (df["history"] < 0).any():
        raise ValueError("Column 'history' contains negative values.")

    if (df["recency"] < 0).any():
        raise ValueError("Column 'recency' contains negative values.")


def reorder_processed_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reorder processed dataset columns into a cleaner analysis-friendly layout.

    Args:
        df: Input dataset.

    Returns:
        pd.DataFrame: Dataset with reordered columns.
    """
    ordered_columns = [
        "customer_id",
        "recency",
        "history_segment",
        "history",
        "mens",
        "womens",
        "zip_code",
        "newbie",
        "channel",
        "segment",
        "campaign_type",
        "binary_treatment_flag",
        "visit",
        "conversion",
        "spend",
    ]
    return df[ordered_columns]


def preprocess_data() -> pd.DataFrame:
    """
    Run the full preprocessing pipeline for the Hillstrom dataset.

    Returns:
        pd.DataFrame: Cleaned and processed dataset ready for downstream use.
    """
    df = load_raw_data()
    validate_raw_columns(df)

    df = clean_history_segment(df)
    df = clean_zip_code(df)

    validate_categorical_values(df)

    df = create_customer_id(df)
    df = create_binary_treatment_flag(df)
    df = create_segment_type(df)

    validate_numeric_columns(df)

    df = reorder_processed_columns(df)
    return df


def save_processed_data(df: pd.DataFrame, output_path: Path | None = None) -> Path:
    """
    Save the processed dataset to the processed data folder.

    Args:
        df: Processed dataset.
        output_path: Optional custom output path.

    Returns:
        Path: File path where the processed data was saved.
    """
    path = output_path if output_path is not None else PROCESSED_DATA_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


def summarize_processed_data(df: pd.DataFrame) -> None:
    """
    Print a concise summary of the processed dataset.

    Args:
        df: Processed dataset.
    """
    print("Processed dataset created successfully.")
    print(f"Shape: {df.shape}")

    print("\nColumns:")
    for column in df.columns:
        print(f"- {column}")

    print("\nSegment distribution:")
    print(df["segment"].value_counts(dropna=False))

    print("\nBinary treatment distribution:")
    print(df["binary_treatment_flag"].value_counts(dropna=False))

    print("\nVisit / conversion / spend means:")
    print(df[["visit", "conversion", "spend"]].mean())

    print("\nFirst 5 rows:")
    print(df.head())

    print("\nzip_code distribution:")
    print(df["zip_code"].value_counts(dropna=False))


def main() -> None:
    """
    Run the preprocessing pipeline and save the processed output.
    """
    df = preprocess_data()
    output_path = save_processed_data(df)
    summarize_processed_data(df)
    print(f"\nProcessed dataset saved to: {output_path}")


if __name__ == "__main__":
    main()