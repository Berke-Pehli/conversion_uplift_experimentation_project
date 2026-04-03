"""
Raw data ingestion utilities for the conversion uplift project.

This module handles the first data-entry step of the project:
loading the canonical Hillstrom CSV dataset from the raw data folder
and validating that the expected source columns are present.

Main responsibilities:
- Locate the raw CSV file
- Load the dataset into a pandas DataFrame
- Validate the expected raw schema
- Print a concise summary for inspection
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
RAW_DATA_FILE = RAW_DATA_DIR / "hillstrom.csv"

EXPECTED_RAW_COLUMNS = [
    "recency",
    "history_segment",
    "history",
    "mens",
    "womens",
    "zip_code",
    "newbie",
    "channel",
    "segment",
    "visit",
    "conversion",
    "spend",
]


def get_raw_data_path() -> Path:
    """
    Return the expected file path of the raw Hillstrom CSV.

    Returns:
        Path: Path to the canonical raw CSV file.
    """
    return RAW_DATA_FILE


def load_raw_data(file_path: Path | None = None) -> pd.DataFrame:
    """
    Load the raw Hillstrom CSV file into a pandas DataFrame.

    Args:
        file_path: Optional custom file path. If not provided, the default
            raw data path is used.

    Returns:
        pd.DataFrame: Loaded raw dataset.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
    """
    path = file_path if file_path is not None else get_raw_data_path()

    if not path.exists():
        raise FileNotFoundError(
            f"Raw data file not found at: {path}\n"
            "Please place hillstrom.csv in data/raw/."
        )

    return pd.read_csv(path)


def validate_raw_columns(df: pd.DataFrame) -> None:
    """
    Validate that the raw dataset contains the expected source columns.

    Args:
        df: Raw dataset.

    Raises:
        ValueError: If required columns are missing.
    """
    actual_columns = set(df.columns)
    expected_columns = set(EXPECTED_RAW_COLUMNS)

    missing_columns = expected_columns - actual_columns
    extra_columns = actual_columns - expected_columns

    if missing_columns:
        raise ValueError(
            "Raw dataset is missing required columns: "
            f"{sorted(missing_columns)}"
        )

    if extra_columns:
        print("Warning: Raw dataset contains unexpected extra columns:")
        print(sorted(extra_columns))


def summarize_raw_data(df: pd.DataFrame) -> None:
    """
    Print a concise summary of the raw dataset.

    Args:
        df: Raw dataset.
    """
    print("Raw dataset loaded successfully.")
    print(f"Shape: {df.shape}")

    print("\nColumns:")
    for column in df.columns:
        print(f"- {column}")

    print("\nDtypes:")
    print(df.dtypes)

    print("\nMissing values:")
    print(df.isna().sum())

    print("\nFirst 5 rows:")
    print(df.head())


def main() -> None:
    """
    Run the raw ingestion validation step.

    This command:
    - loads the raw CSV
    - validates its schema
    - prints a summary for inspection
    """
    df = load_raw_data()
    validate_raw_columns(df)
    summarize_raw_data(df)


if __name__ == "__main__":
    main()