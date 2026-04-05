"""
Pytask task for preprocessing the Hillstrom dataset in the conversion uplift project.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from pytask import Product

from conversion_uplift.config import (
    BLD_DATA_PROCESSED_DIR,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
    create_build_directories,
)
from conversion_uplift.preprocess import preprocess_data, save_processed_data


RAW_DATA_FILE = RAW_DATA_DIR / "hillstrom.csv"
PROCESSED_DATA_FILE = PROCESSED_DATA_DIR / "hillstrom_processed.csv"
BLD_PROCESSED_DATA_FILE = BLD_DATA_PROCESSED_DIR / "hillstrom_processed.csv"


def task_preprocess_data(
    depends_on: Path = RAW_DATA_FILE,
    produces: Annotated[Path, Product] = PROCESSED_DATA_FILE,
) -> None:
    """
    Build the processed Hillstrom dataset from the raw source file.

    The task writes the canonical tracked output to `data/processed/`
    and also writes a reproducible build copy to `bld/data/processed/`.
    """
    _ = depends_on

    create_build_directories()

    processed_df = preprocess_data()

    save_processed_data(processed_df, output_path=produces)
    save_processed_data(processed_df, output_path=BLD_PROCESSED_DATA_FILE)