"""
Export reporting-ready datasets from MySQL views.

This module extracts reporting views from the normalized MySQL schema
and saves them as CSV files for Power BI and downstream analysis.

Main responsibilities:
- Read reporting views from MySQL
- Save clean CSV exports into the final data folder
- Provide a reproducible reporting handoff layer
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from conversion_uplift.database import read_table


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FINAL_DATA_DIR = PROJECT_ROOT / "data" / "final"

EXPORT_CONFIG = {
    "vw_customer_experiment_detail": "customer_experiment_detail.csv",
    "vw_campaign_summary": "campaign_summary.csv",
    "vw_treatment_control_summary": "treatment_control_summary.csv",
    "vw_segment_uplift_summary": "segment_uplift_summary.csv",
    "vw_channel_campaign_summary": "channel_campaign_summary.csv",
    "vw_zip_campaign_summary": "zip_campaign_summary.csv",
    "vw_newbie_campaign_summary": "newbie_campaign_summary.csv",
    "vw_history_segment_campaign_summary": "history_segment_campaign_summary.csv",
}


def export_view_to_csv(view_name: str, output_filename: str) -> Path:
    """
    Export a single MySQL reporting view to a CSV file.

    Args:
        view_name: Name of the MySQL view to export.
        output_filename: Output CSV filename.

    Returns:
        Path: File path of the exported CSV.
    """
    df = read_table(view_name)

    FINAL_DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_path = FINAL_DATA_DIR / output_filename
    df.to_csv(output_path, index=False)

    return output_path


def export_all_reporting_views() -> list[Path]:
    """
    Export all configured reporting views to CSV files.

    Returns:
        list[Path]: List of exported file paths.
    """
    exported_files: list[Path] = []

    for view_name, output_filename in EXPORT_CONFIG.items():
        output_path = export_view_to_csv(view_name, output_filename)
        exported_files.append(output_path)

    return exported_files


def summarize_exports(exported_files: list[Path]) -> None:
    """
    Print a summary of exported reporting files.

    Args:
        exported_files: List of exported file paths.
    """
    print("Reporting exports completed successfully.")
    print("\nExported files:")

    for file_path in exported_files:
        print(f"- {file_path}")


def main() -> None:
    """
    Run the reporting export pipeline.
    """
    exported_files = export_all_reporting_views()
    summarize_exports(exported_files)


if __name__ == "__main__":
    main()