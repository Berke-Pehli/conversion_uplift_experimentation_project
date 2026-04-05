"""
Pytask task for raw data ingestion validation in the conversion uplift project.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import pandas as pd
from pytask import Product

from conversion_uplift.config import (
    BLD_REPORTS_DIR,
    RAW_DATA_DIR,
    REPORTS_DIR,
    create_build_directories,
)
from conversion_uplift.ingest import load_raw_data, validate_raw_columns


RAW_DATA_FILE = RAW_DATA_DIR / "hillstrom.csv"
INGEST_VALIDATION_FILE = REPORTS_DIR / "raw_data_ingestion_summary.csv"
BLD_INGEST_VALIDATION_FILE = BLD_REPORTS_DIR / "raw_data_ingestion_summary.csv"


def task_ingest_data(
    depends_on: Path = RAW_DATA_FILE,
    produces: Annotated[Path, Product] = INGEST_VALIDATION_FILE,
) -> None:
    """
    Validate raw data ingestion and save a small ingestion summary report.

    The task writes the canonical tracked output to `outputs/reports/`
    and also writes a mirrored build copy into `bld/reports/`.
    """
    _ = depends_on

    create_build_directories()

    df = load_raw_data()
    validate_raw_columns(df)

    summary_df = pd.DataFrame(
        {
            "n_rows": [len(df)],
            "n_columns": [df.shape[1]],
            "file_name": [RAW_DATA_FILE.name],
        }
    )

    produces.parent.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(produces, index=False)
    summary_df.to_csv(BLD_INGEST_VALIDATION_FILE, index=False)