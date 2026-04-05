"""
Tests for reporting export utilities in the conversion uplift project.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from conversion_uplift import export


def make_sample_view_df() -> pd.DataFrame:
    """
    Build a small sample reporting view dataset for testing.
    """
    return pd.DataFrame(
        {
            "customer_id": [1, 2, 3],
            "campaign_type": ["control", "mens_email", "womens_email"],
            "conversion_rate": [0.0057, 0.0125, 0.0088],
        }
    )


def test_export_config_contains_expected_reporting_views() -> None:
    """
    The export configuration should contain the expected reporting view names.
    """
    expected_views = {
        "vw_customer_experiment_detail",
        "vw_campaign_summary",
        "vw_treatment_control_summary",
        "vw_segment_uplift_summary",
        "vw_channel_campaign_summary",
        "vw_zip_campaign_summary",
        "vw_newbie_campaign_summary",
        "vw_history_segment_campaign_summary",
    }

    assert set(export.EXPORT_CONFIG.keys()) == expected_views


def test_export_view_to_csv_creates_expected_file(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    Exporting one reporting view should create a CSV with the expected filename.
    """
    sample_df = make_sample_view_df()

    monkeypatch.setattr(export, "FINAL_DATA_DIR", tmp_path)
    monkeypatch.setattr(export, "read_table", lambda view_name: sample_df.copy())

    output_path = export.export_view_to_csv(
        view_name="vw_campaign_summary",
        output_filename="campaign_summary.csv",
    )

    assert output_path.exists()
    assert output_path.name == "campaign_summary.csv"

    result_df = pd.read_csv(output_path)
    pd.testing.assert_frame_equal(result_df, sample_df)


def test_export_all_reporting_views_creates_one_file_per_config_entry(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    Exporting all reporting views should create one output file per configured view.
    """
    sample_df = make_sample_view_df()

    monkeypatch.setattr(export, "FINAL_DATA_DIR", tmp_path)
    monkeypatch.setattr(export, "read_table", lambda view_name: sample_df.copy())

    exported_files = export.export_all_reporting_views()

    assert len(exported_files) == len(export.EXPORT_CONFIG)

    exported_names = {path.name for path in exported_files}
    expected_names = set(export.EXPORT_CONFIG.values())

    assert exported_names == expected_names
    assert all(path.exists() for path in exported_files)


def test_export_all_reporting_views_returns_paths_in_config_order(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    Exporting all views should return paths in the same order as EXPORT_CONFIG.
    """
    sample_df = make_sample_view_df()

    monkeypatch.setattr(export, "FINAL_DATA_DIR", tmp_path)
    monkeypatch.setattr(export, "read_table", lambda view_name: sample_df.copy())

    exported_files = export.export_all_reporting_views()

    expected_order = list(export.EXPORT_CONFIG.values())
    actual_order = [path.name for path in exported_files]

    assert actual_order == expected_order


def test_summarize_exports_prints_expected_header_and_file_names(capsys) -> None:
    """
    Export summary printing should include the success header and file paths.
    """
    exported_files = [
        Path("/tmp/campaign_summary.csv"),
        Path("/tmp/treatment_control_summary.csv"),
    ]

    export.summarize_exports(exported_files)

    captured = capsys.readouterr()
    assert "Reporting exports completed successfully." in captured.out
    assert "campaign_summary.csv" in captured.out
    assert "treatment_control_summary.csv" in captured.out