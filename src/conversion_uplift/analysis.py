"""
Business and modeling-oriented exploratory analysis for the conversion uplift project.

This module analyzes the processed Hillstrom dataset from three business outcome
angles:
- visit
- conversion
- spend

Main responsibilities:
- Load the processed dataset
- Create overall outcome summaries
- Compare treatment vs control outcomes
- Compare original campaign groups
- Build segment-level summaries
- Save clean CSV reports
- Save polished matplotlib charts
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DATA_FILE = PROJECT_ROOT / "data" / "processed" / "hillstrom_processed.csv"

OUTPUTS_REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports"
OUTPUTS_CHARTS_DIR = PROJECT_ROOT / "outputs" / "charts"

SEGMENT_COLUMNS = ["campaign_type", "channel", "zip_code", "history_segment"]


def load_processed_data(file_path: Path | None = None) -> pd.DataFrame:
    """
    Load the processed Hillstrom dataset from disk.

    Args:
        file_path: Optional custom file path.

    Returns:
        pd.DataFrame: Processed dataset.

    Raises:
        FileNotFoundError: If the processed dataset does not exist.
    """
    path = file_path if file_path is not None else PROCESSED_DATA_FILE

    if not path.exists():
        raise FileNotFoundError(
            f"Processed data file not found at: {path}\n"
            "Please run the preprocessing pipeline first."
        )

    return pd.read_csv(path)


def create_output_directories() -> None:
    """
    Create output directories if they do not already exist.
    """
    OUTPUTS_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_CHARTS_DIR.mkdir(parents=True, exist_ok=True)


def apply_chart_style() -> None:
    """
    Apply a consistent clean plotting style.
    """
    plt.rcParams.update(
        {
            "figure.figsize": (8, 5),
            "axes.titlesize": 14,
            "axes.labelsize": 11,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
        }
    )


def build_outcome_overview(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build an overall summary of the three main business outcomes.

    Args:
        df: Processed dataset.

    Returns:
        pd.DataFrame: One-row summary table with core outcome metrics.
    """
    return pd.DataFrame(
        {
            "n_customers": [len(df)],
            "visit_rate": [df["visit"].mean()],
            "conversion_rate": [df["conversion"].mean()],
            "average_spend": [df["spend"].mean()],
            "total_spend": [df["spend"].sum()],
            "average_spend_per_converter": [
                df.loc[df["conversion"] == 1, "spend"].mean()
            ],
        }
    )


def build_treatment_control_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compare treatment vs control outcomes using the binary treatment flag.

    Args:
        df: Processed dataset.

    Returns:
        pd.DataFrame: Treatment/control comparison summary.
    """
    summary = (
        df.groupby("binary_treatment_flag", as_index=False)
        .agg(
            customers=("customer_id", "count"),
            visit_rate=("visit", "mean"),
            conversion_rate=("conversion", "mean"),
            average_spend=("spend", "mean"),
            total_spend=("spend", "sum"),
        )
        .sort_values("binary_treatment_flag")
    )

    summary["treatment_group"] = summary["binary_treatment_flag"].map(
        {0: "control", 1: "treatment"}
    )

    ordered_columns = [
        "binary_treatment_flag",
        "treatment_group",
        "customers",
        "visit_rate",
        "conversion_rate",
        "average_spend",
        "total_spend",
    ]
    return summary[ordered_columns]


def build_campaign_type_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compare original campaign groups across the three main outcomes.

    Args:
        df: Processed dataset.

    Returns:
        pd.DataFrame: Campaign-type summary table.
    """
    campaign_order = ["control", "womens_email", "mens_email"]

    summary = (
        df.groupby("campaign_type", as_index=False)
        .agg(
            customers=("customer_id", "count"),
            visit_rate=("visit", "mean"),
            conversion_rate=("conversion", "mean"),
            average_spend=("spend", "mean"),
            total_spend=("spend", "sum"),
        )
    )

    summary["campaign_type"] = pd.Categorical(
        summary["campaign_type"],
        categories=campaign_order,
        ordered=True,
    )

    return summary.sort_values("campaign_type").reset_index(drop=True)


def build_segment_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a stacked segment summary across several grouping dimensions.

    Args:
        df: Processed dataset.

    Returns:
        pd.DataFrame: Combined segment summary table.
    """
    segment_frames: list[pd.DataFrame] = []

    for segment_column in SEGMENT_COLUMNS:
        grouped = (
            df.groupby(segment_column, as_index=False)
            .agg(
                customers=("customer_id", "count"),
                visit_rate=("visit", "mean"),
                conversion_rate=("conversion", "mean"),
                average_spend=("spend", "mean"),
                total_spend=("spend", "sum"),
            )
            .rename(columns={segment_column: "segment_value"})
        )

        grouped.insert(0, "segment_type", segment_column)
        segment_frames.append(grouped)

    return pd.concat(segment_frames, ignore_index=True)


def save_dataframe(df: pd.DataFrame, filename: str) -> Path:
    """
    Save a DataFrame as CSV in the reports output folder.

    Args:
        df: DataFrame to save.
        filename: Output filename.

    Returns:
        Path: Saved file path.
    """
    output_path = OUTPUTS_REPORTS_DIR / filename
    df.to_csv(output_path, index=False)
    return output_path


def add_bar_labels(ax: plt.Axes, fmt: str = "{:.3f}") -> None:
    """
    Add numeric labels above bar-chart bars.

    Args:
        ax: Matplotlib axes object.
        fmt: Number format string.
    """
    for patch in ax.patches:
        height = patch.get_height()
        ax.annotate(
            fmt.format(height),
            (patch.get_x() + patch.get_width() / 2, height),
            ha="center",
            va="bottom",
            xytext=(0, 4),
            textcoords="offset points",
        )


def plot_campaign_outcome_rates(campaign_summary: pd.DataFrame) -> list[Path]:
    """
    Create polished bar charts for campaign-level outcomes.

    Args:
        campaign_summary: Campaign-level summary table.

    Returns:
        list[Path]: List of saved chart paths.
    """
    saved_paths: list[Path] = []

    chart_specs = [
        ("visit_rate", "visit_rate_by_campaign_type.png", "Visit Rate by Campaign Type", "{:.3f}"),
        (
            "conversion_rate",
            "conversion_rate_by_campaign_type.png",
            "Conversion Rate by Campaign Type",
            "{:.4f}",
        ),
        (
            "average_spend",
            "average_spend_by_campaign_type.png",
            "Average Spend by Campaign Type",
            "{:.2f}",
        ),
    ]

    for metric_column, filename, title, fmt in chart_specs:
        fig, ax = plt.subplots()
        ax.bar(campaign_summary["campaign_type"].astype(str), campaign_summary[metric_column])
        ax.set_title(title)
        ax.set_xlabel("Campaign Type")
        ax.set_ylabel(metric_column.replace("_", " ").title())
        ax.tick_params(axis="x", rotation=15)
        add_bar_labels(ax, fmt=fmt)
        fig.tight_layout()

        output_path = OUTPUTS_CHARTS_DIR / filename
        fig.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close(fig)

        saved_paths.append(output_path)

    return saved_paths


def plot_single_treatment_control_dumbbell(
    treatment_summary: pd.DataFrame,
    metric_column: str,
    filename: str,
    title: str,
    fmt: str,
) -> Path:
    """
    Create a polished single-metric dumbbell chart for treatment vs control.

    Args:
        treatment_summary: Treatment/control summary table.
        metric_column: Metric column to compare.
        filename: Output filename.
        title: Chart title.
        fmt: Value format string.

    Returns:
        Path: Saved chart path.
    """
    control_value = treatment_summary.loc[
        treatment_summary["treatment_group"] == "control", metric_column
    ].iloc[0]

    treatment_value = treatment_summary.loc[
        treatment_summary["treatment_group"] == "treatment", metric_column
    ].iloc[0]

    fig, ax = plt.subplots(figsize=(7, 2.8))
    ax.plot([control_value, treatment_value], [0, 0], linewidth=2)
    ax.scatter(control_value, 0, s=100, label="control")
    ax.scatter(treatment_value, 0, s=100, label="treatment")

    ax.annotate(
        fmt.format(control_value),
        (control_value, 0),
        xytext=(0, 10),
        textcoords="offset points",
        ha="center",
    )
    ax.annotate(
        fmt.format(treatment_value),
        (treatment_value, 0),
        xytext=(0, 10),
        textcoords="offset points",
        ha="center",
    )

    ax.set_yticks([])
    ax.set_xlabel(metric_column.replace("_", " ").title())
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()

    output_path = OUTPUTS_CHARTS_DIR / filename
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    return output_path


def plot_segment_outcome_heatmap_normalized(segment_summary: pd.DataFrame) -> Path:
    """
    Create a column-wise normalized heatmap so metrics with different scales
    can be compared visually.

    Args:
        segment_summary: Combined segment summary table.

    Returns:
        Path: Saved chart path.
    """
    heatmap_df = segment_summary.copy()
    heatmap_df["segment_label"] = (
        heatmap_df["segment_type"] + " | " + heatmap_df["segment_value"].astype(str)
    )

    heatmap_df = heatmap_df[
        ["segment_label", "visit_rate", "conversion_rate", "average_spend"]
    ].set_index("segment_label")

    normalized_df = heatmap_df.copy()

    for column in normalized_df.columns:
        col_min = normalized_df[column].min()
        col_max = normalized_df[column].max()

        if col_max > col_min:
            normalized_df[column] = (normalized_df[column] - col_min) / (
                col_max - col_min
            )
        else:
            normalized_df[column] = 0.0

    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(normalized_df.values, aspect="auto")
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Normalized Intensity")
    ax.set_xticks(range(len(normalized_df.columns)))
    ax.set_xticklabels(normalized_df.columns, rotation=15)
    ax.set_yticks(range(len(normalized_df.index)))
    ax.set_yticklabels(normalized_df.index)
    ax.set_title("Segment Outcome Heatmap (Normalized by Metric)")
    fig.tight_layout()

    output_path = OUTPUTS_CHARTS_DIR / "segment_outcome_heatmap_normalized.png"
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    return output_path


def plot_ranked_history_segment_chart(
    segment_summary: pd.DataFrame,
    metric_column: str,
    filename: str,
    title: str,
    fmt: str,
) -> Path:
    """
    Create a ranked horizontal bar chart for history segments.

    Args:
        segment_summary: Combined segment summary table.
        metric_column: Metric to plot.
        filename: Output filename.
        title: Chart title.
        fmt: Value format string.

    Returns:
        Path: Saved chart path.
    """
    history_df = segment_summary.loc[
        segment_summary["segment_type"] == "history_segment"
    ].copy()

    history_df = history_df.sort_values(metric_column, ascending=True)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(history_df["segment_value"], history_df[metric_column])
    ax.set_title(title)
    ax.set_xlabel(metric_column.replace("_", " ").title())
    ax.set_ylabel("History Segment")

    for patch in ax.patches:
        width = patch.get_width()
        ax.annotate(
            fmt.format(width),
            (width, patch.get_y() + patch.get_height() / 2),
            va="center",
            ha="left",
            xytext=(4, 0),
            textcoords="offset points",
        )

    fig.tight_layout()

    output_path = OUTPUTS_CHARTS_DIR / filename
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    return output_path


def plot_campaign_outcome_bubble(campaign_summary: pd.DataFrame) -> Path:
    """
    Create a polished bubble chart comparing campaign types across outcomes.

    Args:
        campaign_summary: Campaign-level summary table.

    Returns:
        Path: Saved chart path.
    """
    bubble_sizes = campaign_summary["average_spend"] * 900

    fig, ax = plt.subplots()
    ax.scatter(
        campaign_summary["visit_rate"],
        campaign_summary["conversion_rate"],
        s=bubble_sizes,
        alpha=0.6,
    )

    for _, row in campaign_summary.iterrows():
        ax.annotate(
            row["campaign_type"],
            (row["visit_rate"], row["conversion_rate"]),
            xytext=(5, 5),
            textcoords="offset points",
        )

    ax.set_xlabel("Visit Rate")
    ax.set_ylabel("Conversion Rate")
    ax.set_title("Campaign Comparison Bubble Chart")
    fig.tight_layout()

    output_path = OUTPUTS_CHARTS_DIR / "campaign_outcome_bubble.png"
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    return output_path


def summarize_analysis_results(
    outcome_overview_path: Path,
    treatment_control_path: Path,
    campaign_summary_path: Path,
    segment_summary_path: Path,
    chart_paths: list[Path],
) -> None:
    """
    Print a summary of saved analysis outputs.

    Args:
        outcome_overview_path: Path to overall outcome summary CSV.
        treatment_control_path: Path to treatment/control summary CSV.
        campaign_summary_path: Path to campaign summary CSV.
        segment_summary_path: Path to segment summary CSV.
        chart_paths: List of saved chart paths.
    """
    print("Python analysis completed successfully.")
    print("\nSaved report files:")
    print(f"- {outcome_overview_path}")
    print(f"- {treatment_control_path}")
    print(f"- {campaign_summary_path}")
    print(f"- {segment_summary_path}")

    print("\nSaved chart files:")
    for chart_path in chart_paths:
        print(f"- {chart_path}")


def main() -> None:
    """
    Run the Python business-analysis pipeline on the processed dataset.
    """
    create_output_directories()
    apply_chart_style()

    df = load_processed_data()

    outcome_overview = build_outcome_overview(df)
    treatment_control_summary = build_treatment_control_summary(df)
    campaign_summary = build_campaign_type_summary(df)
    segment_summary = build_segment_summary(df)

    outcome_overview_path = save_dataframe(
        outcome_overview, "python_outcome_overview.csv"
    )
    treatment_control_path = save_dataframe(
        treatment_control_summary, "python_treatment_control_summary.csv"
    )
    campaign_summary_path = save_dataframe(
        campaign_summary, "python_campaign_type_summary.csv"
    )
    segment_summary_path = save_dataframe(
        segment_summary, "python_segment_summary.csv"
    )

    chart_paths = []
    chart_paths.extend(plot_campaign_outcome_rates(campaign_summary))

    chart_paths.append(
        plot_single_treatment_control_dumbbell(
            treatment_summary=treatment_control_summary,
            metric_column="visit_rate",
            filename="treatment_control_visit_rate_dumbbell.png",
            title="Treatment vs Control: Visit Rate",
            fmt="{:.3f}",
        )
    )
    chart_paths.append(
        plot_single_treatment_control_dumbbell(
            treatment_summary=treatment_control_summary,
            metric_column="conversion_rate",
            filename="treatment_control_conversion_rate_dumbbell.png",
            title="Treatment vs Control: Conversion Rate",
            fmt="{:.4f}",
        )
    )
    chart_paths.append(
        plot_single_treatment_control_dumbbell(
            treatment_summary=treatment_control_summary,
            metric_column="average_spend",
            filename="treatment_control_average_spend_dumbbell.png",
            title="Treatment vs Control: Average Spend",
            fmt="{:.2f}",
        )
    )

    chart_paths.append(plot_segment_outcome_heatmap_normalized(segment_summary))

    chart_paths.append(
        plot_ranked_history_segment_chart(
            segment_summary=segment_summary,
            metric_column="conversion_rate",
            filename="history_segment_conversion_rate_ranked.png",
            title="History Segment Ranking by Conversion Rate",
            fmt="{:.4f}",
        )
    )
    chart_paths.append(
        plot_ranked_history_segment_chart(
            segment_summary=segment_summary,
            metric_column="average_spend",
            filename="history_segment_average_spend_ranked.png",
            title="History Segment Ranking by Average Spend",
            fmt="{:.2f}",
        )
    )

    chart_paths.append(plot_campaign_outcome_bubble(campaign_summary))

    summarize_analysis_results(
        outcome_overview_path=outcome_overview_path,
        treatment_control_path=treatment_control_path,
        campaign_summary_path=campaign_summary_path,
        segment_summary_path=segment_summary_path,
        chart_paths=chart_paths,
    )


if __name__ == "__main__":
    main()