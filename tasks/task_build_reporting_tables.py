"""
Pytask task for exporting reporting-ready tables in the conversion uplift project.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import pandas as pd
from pytask import Product

from conversion_uplift.export import EXPORT_CONFIG, export_all_reporting_views


PROJECT_ROOT = Path(__file__).resolve().parents[1]

MYSQL_LOAD_SUMMARY_FILE = PROJECT_ROOT / "outputs" / "reports" / "mysql_load_summary.csv"
REPORTING_EXPORT_SUMMARY_FILE = (
    PROJECT_ROOT / "outputs" / "reports" / "reporting_export_summary.csv"
)


def task_build_reporting_tables(
    depends_on: Path = MYSQL_LOAD_SUMMARY_FILE,
    produces: Annotated[Path, Product] = REPORTING_EXPORT_SUMMARY_FILE,
) -> None:
    """
    Export reporting-ready CSV files from MySQL views and save a summary report.
    """
    _ = depends_on

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