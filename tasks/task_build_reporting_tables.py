"""
Pytask task for exporting reporting-ready tables in the conversion uplift project.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Annotated

import pandas as pd
from pytask import Product

from conversion_uplift.config import (
    BLD_DATA_FINAL_DIR,
    BLD_REPORTS_DIR,
    REPORTS_DIR,
    create_build_directories,
)
from conversion_uplift.export import EXPORT_CONFIG, export_all_reporting_views


MYSQL_LOAD_SUMMARY_FILE = REPORTS_DIR / "mysql_load_summary.csv"
REPORTING_EXPORT_SUMMARY_FILE = REPORTS_DIR / "reporting_export_summary.csv"
BLD_REPORTING_EXPORT_SUMMARY_FILE = BLD_REPORTS_DIR / "reporting_export_summary.csv"


def task_build_reporting_tables(
    depends_on: Path = MYSQL_LOAD_SUMMARY_FILE,
    produces: Annotated[Path, Product] = REPORTING_EXPORT_SUMMARY_FILE,
) -> None:
    """
    Export reporting-ready CSV files from MySQL views and save a summary report.

    The task writes the canonical tracked output to `outputs/reports/`
    and also writes mirrored build copies into `bld/`.
    """
    _ = depends_on

    create_build_directories()

    exported_files = export_all_reporting_views()

    summary_df = pd.DataFrame(
        {
            "n_exported_files": [len(exported_files)],
            "exported_view_names": [", ".join(EXPORT_CONFIG.keys())],
            "exported_file_names": [", ".join(path.name for path in exported_files)],
        }
    )

    produces.parent.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(produces, index=False)
    summary_df.to_csv(BLD_REPORTING_EXPORT_SUMMARY_FILE, index=False)

    for exported_file in exported_files:
        shutil.copy2(exported_file, BLD_DATA_FINAL_DIR / exported_file.name)