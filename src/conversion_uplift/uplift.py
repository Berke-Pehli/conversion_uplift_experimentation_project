"""
Refined uplift modeling pipeline for the conversion uplift project.

This module builds a treatment-aware uplift workflow using a simple
two-model approach for the conversion outcome.

Main responsibilities:
- Load encoded features and conversion targets
- Separate treatment and control groups
- Train one model on treated customers and one on control customers
- Estimate individual uplift scores
- Summarize uplift by decile and by selected segments
- Include observed uplift validation columns
- Save uplift outputs and charts
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LogisticRegression


PROJECT_ROOT = Path(__file__).resolve().parents[2]

FINAL_DATA_DIR = PROJECT_ROOT / "data" / "final"
OUTPUTS_REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports"
OUTPUTS_CHARTS_DIR = PROJECT_ROOT / "outputs" / "charts"

FEATURES_FILE = FINAL_DATA_DIR / "modeling_features_encoded.csv"
BASE_DATASET_FILE = FINAL_DATA_DIR / "modeling_base_dataset.csv"
TARGET_CONVERSION_FILE = FINAL_DATA_DIR / "modeling_target_conversion.csv"

RANDOM_STATE = 42
N_DECILES = 10


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


def load_csv(path: Path) -> pd.DataFrame:
    """
    Load a CSV file from disk.

    Args:
        path: Path to the CSV file.

    Returns:
        pd.DataFrame: Loaded DataFrame.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")
    return pd.read_csv(path)


def load_uplift_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load feature, base, and conversion target datasets.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
            Encoded features, modeling base dataset, conversion targets.
    """
    features_df = load_csv(FEATURES_FILE)
    base_df = load_csv(BASE_DATASET_FILE)
    conversion_df = load_csv(TARGET_CONVERSION_FILE)

    return features_df, base_df, conversion_df


def prepare_uplift_dataset(
    features_df: pd.DataFrame,
    base_df: pd.DataFrame,
    conversion_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Merge feature and target information into one uplift-scoring dataset.

    Args:
        features_df: Encoded feature dataset.
        base_df: Base modeling dataset.
        conversion_df: Conversion target dataset.

    Returns:
        pd.DataFrame: Combined uplift dataset.
    """
    df = features_df.merge(
        conversion_df,
        on="customer_id",
        how="inner",
    )

    merge_columns = [
        "customer_id",
        "segment",
        "campaign_type",
        "history_segment",
        "zip_code",
        "channel",
        "binary_treatment_flag",
    ]

    df = df.merge(
        base_df[merge_columns],
        on=["customer_id", "binary_treatment_flag"],
        how="inner",
    )

    return df


def get_feature_columns(df: pd.DataFrame) -> list[str]:
    """
    Get feature columns for uplift modeling.

    We exclude:
    - customer_id
    - observed target
    - descriptive/raw reporting columns

    Args:
        df: Uplift dataset.

    Returns:
        list[str]: Modeling feature columns.
    """
    excluded_columns = {
        "customer_id",
        "conversion",
        "segment",
        "campaign_type",
        "history_segment",
        "zip_code",
        "channel",
    }

    return [column for column in df.columns if column not in excluded_columns]


def train_two_model_uplift(df: pd.DataFrame) -> pd.DataFrame:
    """
    Train separate treated/control models and score uplift for all customers.

    Args:
        df: Uplift dataset.

    Returns:
        pd.DataFrame: Customer-level uplift scoring output.
    """
    feature_columns = get_feature_columns(df)

    treated_df = df.loc[df["binary_treatment_flag"] == 1].copy()
    control_df = df.loc[df["binary_treatment_flag"] == 0].copy()

    X_treated = treated_df[feature_columns]
    y_treated = treated_df["conversion"]

    X_control = control_df[feature_columns]
    y_control = control_df["conversion"]

    treated_model = LogisticRegression(
        max_iter=1000,
        random_state=RANDOM_STATE,
        class_weight="balanced",
    )
    control_model = LogisticRegression(
        max_iter=1000,
        random_state=RANDOM_STATE,
        class_weight="balanced",
    )

    treated_model.fit(X_treated, y_treated)
    control_model.fit(X_control, y_control)

    X_all = df[feature_columns]

    scored_df = df[
        [
            "customer_id",
            "segment",
            "campaign_type",
            "history_segment",
            "zip_code",
            "channel",
            "binary_treatment_flag",
            "conversion",
        ]
    ].copy()

    scored_df["pred_conversion_if_treated"] = treated_model.predict_proba(X_all)[:, 1]
    scored_df["pred_conversion_if_control"] = control_model.predict_proba(X_all)[:, 1]
    scored_df["uplift_score"] = (
        scored_df["pred_conversion_if_treated"]
        - scored_df["pred_conversion_if_control"]
    )

    scored_df = scored_df.sort_values(
        "uplift_score",
        ascending=False,
    ).reset_index(drop=True)

    return scored_df


def add_uplift_deciles(scored_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add uplift decile labels to the scored uplift dataset.

    Args:
        scored_df: Customer-level uplift scoring output.

    Returns:
        pd.DataFrame: Scored dataset with uplift deciles.
    """
    decile_df = scored_df.copy()
    decile_df["uplift_decile"] = pd.qcut(
        decile_df.index + 1,
        q=N_DECILES,
        labels=[f"D{i}" for i in range(1, N_DECILES + 1)],
    )
    return decile_df


def build_uplift_decile_summary(scored_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build uplift summary by predicted uplift decile, including observed uplift.

    Args:
        scored_df: Customer-level uplift scoring output.

    Returns:
        pd.DataFrame: Decile-level uplift summary.
    """
    decile_df = add_uplift_deciles(scored_df)

    summary = (
        decile_df.groupby("uplift_decile", as_index=False)
        .agg(
            customers=("customer_id", "count"),
            avg_uplift_score=("uplift_score", "mean"),
            avg_pred_treated=("pred_conversion_if_treated", "mean"),
            avg_pred_control=("pred_conversion_if_control", "mean"),
            observed_conversion_rate=("conversion", "mean"),
        )
    )

    treated_summary = (
        decile_df.loc[decile_df["binary_treatment_flag"] == 1]
        .groupby("uplift_decile", as_index=False)
        .agg(
            treated_customers=("customer_id", "count"),
            treated_conversion_rate=("conversion", "mean"),
        )
    )

    control_summary = (
        decile_df.loc[decile_df["binary_treatment_flag"] == 0]
        .groupby("uplift_decile", as_index=False)
        .agg(
            control_customers=("customer_id", "count"),
            control_conversion_rate=("conversion", "mean"),
        )
    )

    summary = summary.merge(treated_summary, on="uplift_decile", how="left")
    summary = summary.merge(control_summary, on="uplift_decile", how="left")

    summary["treated_customers"] = summary["treated_customers"].fillna(0).astype(int)
    summary["control_customers"] = summary["control_customers"].fillna(0).astype(int)
    summary["treated_conversion_rate"] = summary["treated_conversion_rate"].fillna(0.0)
    summary["control_conversion_rate"] = summary["control_conversion_rate"].fillna(0.0)
    summary["observed_uplift"] = (
        summary["treated_conversion_rate"] - summary["control_conversion_rate"]
    )

    return summary


def build_segment_uplift_summary(scored_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build uplift summary by selected business segments, including observed uplift.

    Args:
        scored_df: Customer-level uplift scoring output.

    Returns:
        pd.DataFrame: Segment-level uplift summary.
    """
    segment_frames: list[pd.DataFrame] = []

    for segment_column in ["campaign_type", "history_segment", "zip_code", "channel"]:
        base_summary = (
            scored_df.groupby(segment_column, as_index=False)
            .agg(
                customers=("customer_id", "count"),
                avg_uplift_score=("uplift_score", "mean"),
                avg_pred_treated=("pred_conversion_if_treated", "mean"),
                avg_pred_control=("pred_conversion_if_control", "mean"),
                observed_conversion_rate=("conversion", "mean"),
            )
            .rename(columns={segment_column: "segment_value"})
        )

        treated_summary = (
            scored_df.loc[scored_df["binary_treatment_flag"] == 1]
            .groupby(segment_column, as_index=False)
            .agg(
                treated_customers=("customer_id", "count"),
                treated_conversion_rate=("conversion", "mean"),
            )
            .rename(columns={segment_column: "segment_value"})
        )

        control_summary = (
            scored_df.loc[scored_df["binary_treatment_flag"] == 0]
            .groupby(segment_column, as_index=False)
            .agg(
                control_customers=("customer_id", "count"),
                control_conversion_rate=("conversion", "mean"),
            )
            .rename(columns={segment_column: "segment_value"})
        )

        grouped = base_summary.merge(treated_summary, on="segment_value", how="left")
        grouped = grouped.merge(control_summary, on="segment_value", how="left")

        grouped["treated_customers"] = grouped["treated_customers"].fillna(0).astype(int)
        grouped["control_customers"] = grouped["control_customers"].fillna(0).astype(int)
        grouped["treated_conversion_rate"] = grouped["treated_conversion_rate"].fillna(0.0)
        grouped["control_conversion_rate"] = grouped["control_conversion_rate"].fillna(0.0)
        grouped["observed_uplift"] = (
            grouped["treated_conversion_rate"] - grouped["control_conversion_rate"]
        )

        grouped.insert(0, "segment_type", segment_column)
        segment_frames.append(grouped)

    return pd.concat(segment_frames, ignore_index=True)


def save_dataframe(df: pd.DataFrame, output_path: Path) -> Path:
    """
    Save a DataFrame to CSV.

    Args:
        df: DataFrame to save.
        output_path: Destination path.

    Returns:
        Path: Saved path.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return output_path


def add_bar_labels(ax: plt.Axes, fmt: str = "{:.4f}") -> None:
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


def plot_uplift_by_decile(decile_summary: pd.DataFrame) -> Path:
    """
    Plot average uplift score by uplift decile.

    Args:
        decile_summary: Decile-level uplift summary.

    Returns:
        Path: Saved chart path.
    """
    fig, ax = plt.subplots()
    ax.bar(decile_summary["uplift_decile"], decile_summary["avg_uplift_score"])
    ax.set_title("Average Predicted Uplift by Decile")
    ax.set_xlabel("Uplift Decile")
    ax.set_ylabel("Average Uplift Score")
    add_bar_labels(ax, fmt="{:.4f}")
    fig.tight_layout()

    output_path = OUTPUTS_CHARTS_DIR / "uplift_by_decile.png"
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    return output_path


def plot_observed_uplift_by_decile(decile_summary: pd.DataFrame) -> Path:
    """
    Plot observed uplift by uplift decile.

    Args:
        decile_summary: Decile-level uplift summary.

    Returns:
        Path: Saved chart path.
    """
    fig, ax = plt.subplots()
    ax.bar(decile_summary["uplift_decile"], decile_summary["observed_uplift"])
    ax.set_title("Observed Uplift by Decile")
    ax.set_xlabel("Uplift Decile")
    ax.set_ylabel("Observed Uplift")
    add_bar_labels(ax, fmt="{:.4f}")
    fig.tight_layout()

    output_path = OUTPUTS_CHARTS_DIR / "observed_uplift_by_decile.png"
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    return output_path


def plot_uplift_score_distribution(scored_df: pd.DataFrame) -> Path:
    """
    Plot the distribution of uplift scores.

    Args:
        scored_df: Customer-level uplift scoring output.

    Returns:
        Path: Saved chart path.
    """
    fig, ax = plt.subplots()
    ax.hist(scored_df["uplift_score"], bins=30)
    ax.set_title("Uplift Score Distribution")
    ax.set_xlabel("Uplift Score")
    ax.set_ylabel("Customer Count")
    fig.tight_layout()

    output_path = OUTPUTS_CHARTS_DIR / "uplift_score_distribution.png"
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    return output_path


def summarize_outputs(saved_paths: list[Path]) -> None:
    """
    Print a summary of saved uplift outputs.

    Args:
        saved_paths: List of saved output paths.
    """
    print("Refined uplift modeling completed successfully.")
    print("\nSaved files:")

    for path in saved_paths:
        print(f"- {path}")


def main() -> None:
    """
    Run the refined uplift modeling pipeline.
    """
    create_output_directories()
    apply_chart_style()

    features_df, base_df, conversion_df = load_uplift_inputs()
    uplift_df = prepare_uplift_dataset(features_df, base_df, conversion_df)

    scored_df = train_two_model_uplift(uplift_df)
    decile_summary_df = build_uplift_decile_summary(scored_df)
    segment_summary_df = build_segment_uplift_summary(scored_df)

    saved_paths: list[Path] = []

    saved_paths.append(
        save_dataframe(
            scored_df,
            OUTPUTS_REPORTS_DIR / "uplift_conversion_scored.csv",
        )
    )
    saved_paths.append(
        save_dataframe(
            decile_summary_df,
            OUTPUTS_REPORTS_DIR / "uplift_conversion_decile_summary.csv",
        )
    )
    saved_paths.append(
        save_dataframe(
            segment_summary_df,
            OUTPUTS_REPORTS_DIR / "uplift_segment_summary.csv",
        )
    )

    saved_paths.append(plot_uplift_by_decile(decile_summary_df))
    saved_paths.append(plot_observed_uplift_by_decile(decile_summary_df))
    saved_paths.append(plot_uplift_score_distribution(scored_df))

    summarize_outputs(saved_paths)


if __name__ == "__main__":
    main()