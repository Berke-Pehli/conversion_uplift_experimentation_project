"""
Pytask task for preprocessing the Hillstrom dataset in the conversion uplift project.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from pytask import Product

from conversion_uplift.preprocess import preprocess_data, save_processed_data


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_FILE = PROJECT_ROOT / "data" / "raw" / "hillstrom.csv"
PROCESSED_DATA_FILE = PROJECT_ROOT / "data" / "processed" / "hillstrom_processed.csv"


def task_preprocess_data(
    depends_on: Path = RAW_DATA_FILE,
    produces: Annotated[Path, Product] = PROCESSED_DATA_FILE,
) -> None:
    """
    Build the processed Hillstrom dataset from the raw source file.
    """
    _ = depends_on

    processed_df = preprocess_data()
    save_processed_data(processed_df, output_path=produces)