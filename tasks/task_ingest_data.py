"""
Pytask task for raw data ingestion validation in the conversion uplift project.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import pandas as pd
from pytask import Product

from conversion_uplift.ingest import load_raw_data, validate_raw_columns


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_FILE = PROJECT_ROOT / "data" / "raw" / "hillstrom.csv"
INGEST_VALIDATION_FILE = PROJECT_ROOT / "outputs" / "reports" / "raw_data_ingestion_summary.csv"


def task_ingest_data(
    depends_on: Path = RAW_DATA_FILE,
    produces: Annotated[Path, Product] = INGEST_VALIDATION_FILE,
) -> None:
    """
    Validate raw data ingestion and save a small ingestion summary report.
    """
    _ = depends_on

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