"""
Refined baseline modeling pipeline for the conversion uplift project.

This module trains and compares baseline models for three business outcomes:
- conversion (classification)
- visit (classification)
- spend (regression)

Main responsibilities:
- Load encoded modeling features and target files
- Train/test split the data
- Fit baseline classification and regression models
- Evaluate model performance with imbalance-aware metrics
- Save metric summaries and comparison charts
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
    root_mean_squared_error,
)
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor


PROJECT_ROOT = Path(__file__).resolve().parents[2]

FINAL_DATA_DIR = PROJECT_ROOT / "data" / "final"
OUTPUTS_REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports"
OUTPUTS_CHARTS_DIR = PROJECT_ROOT / "outputs" / "charts"

FEATURES_FILE = FINAL_DATA_DIR / "modeling_features_encoded.csv"
TARGET_CONVERSION_FILE = FINAL_DATA_DIR / "modeling_target_conversion.csv"
TARGET_VISIT_FILE = FINAL_DATA_DIR / "modeling_target_visit.csv"
TARGET_SPEND_FILE = FINAL_DATA_DIR / "modeling_target_spend.csv"

RANDOM_STATE = 42
TEST_SIZE = 0.2


def create_output_directories() -> None:
    """
    Create output directories if they do not already exist.
    """
    OUTPUTS_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_CHARTS_DIR.mkdir(parents=True, exist_ok=True)


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


def load_modeling_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load encoded features and target datasets.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
            Features, conversion target, visit target, spend target.
    """
    features_df = load_csv(FEATURES_FILE)
    conversion_df = load_csv(TARGET_CONVERSION_FILE)
    visit_df = load_csv(TARGET_VISIT_FILE)
    spend_df = load_csv(TARGET_SPEND_FILE)

    return features_df, conversion_df, visit_df, spend_df


def prepare_feature_matrix(features_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """
    Prepare the feature matrix for modeling.

    Args:
        features_df: Encoded feature DataFrame including customer_id.

    Returns:
        tuple[pd.DataFrame, pd.Series]:
            Feature matrix X and customer_id series.
    """
    customer_ids = features_df["customer_id"].copy()
    X = features_df.drop(columns=["customer_id"]).copy()
    return X, customer_ids


def prepare_target_series(target_df: pd.DataFrame, target_column: str) -> pd.Series:
    """
    Extract the target series from a target DataFrame.

    Args:
        target_df: Target DataFrame with customer_id and target column.
        target_column: Name of the target column.

    Returns:
        pd.Series: Target series.
    """
    return target_df[target_column].copy()


def evaluate_classification_models(
    X: pd.DataFrame,
    y: pd.Series,
    target_name: str,
) -> pd.DataFrame:
    """
    Train and evaluate imbalance-aware classification models.

    Args:
        X: Feature matrix.
        y: Target series.
        target_name: Target name for reporting.

    Returns:
        pd.DataFrame: Classification model evaluation summary.
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    models = {
        "logistic_regression_balanced": LogisticRegression(
            max_iter=1000,
            random_state=RANDOM_STATE,
            class_weight="balanced",
        ),
        "decision_tree_classifier_balanced": DecisionTreeClassifier(
            random_state=RANDOM_STATE,
            class_weight="balanced",
        ),
        "random_forest_classifier_balanced": RandomForestClassifier(
            n_estimators=200,
            random_state=RANDOM_STATE,
            n_jobs=-1,
            class_weight="balanced",
        ),
    }

    results: list[dict[str, float | int | str]] = []

    for model_name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        if hasattr(model, "predict_proba"):
            y_score = model.predict_proba(X_test)[:, 1]
        else:
            y_score = y_pred

        tn, fp, fn, tp = confusion_matrix(y_test, y_pred, labels=[0, 1]).ravel()

        results.append(
            {
                "target": target_name,
                "model_name": model_name,
                "accuracy": accuracy_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred, zero_division=0),
                "recall": recall_score(y_test, y_pred, zero_division=0),
                "f1_score": f1_score(y_test, y_pred, zero_division=0),
                "roc_auc": roc_auc_score(y_test, y_score),
                "pr_auc": average_precision_score(y_test, y_score),
                "positive_prediction_rate": float((y_pred == 1).mean()),
                "true_negative": int(tn),
                "false_positive": int(fp),
                "false_negative": int(fn),
                "true_positive": int(tp),
            }
        )

    results_df = pd.DataFrame(results).sort_values(
        by="pr_auc", ascending=False
    ).reset_index(drop=True)

    return results_df


def evaluate_regression_models(
    X: pd.DataFrame,
    y: pd.Series,
    target_name: str,
) -> pd.DataFrame:
    """
    Train and evaluate baseline regression models.

    Args:
        X: Feature matrix.
        y: Target series.
        target_name: Target name for reporting.

    Returns:
        pd.DataFrame: Regression model evaluation summary.
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
    )

    models = {
        "linear_regression": LinearRegression(),
        "decision_tree_regressor": DecisionTreeRegressor(random_state=RANDOM_STATE),
        "random_forest_regressor": RandomForestRegressor(
            n_estimators=200,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
    }

    results: list[dict[str, float | str]] = []

    for model_name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        rmse = root_mean_squared_error(y_test, y_pred)

        results.append(
            {
                "target": target_name,
                "model_name": model_name,
                "rmse": rmse,
                "mae": mean_absolute_error(y_test, y_pred),
                "r2_score": r2_score(y_test, y_pred),
            }
        )

    results_df = pd.DataFrame(results).sort_values(
        by="rmse", ascending=True
    ).reset_index(drop=True)

    return results_df


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


def plot_classification_metric_comparison(
    results_df: pd.DataFrame,
    metric_column: str,
    filename: str,
    title: str,
) -> Path:
    """
    Plot a classification metric comparison chart.

    Args:
        results_df: Classification results DataFrame.
        metric_column: Metric column to plot.
        filename: Output filename.
        title: Chart title.

    Returns:
        Path: Saved chart path.
    """
    plt.figure(figsize=(8, 5))
    plt.bar(results_df["model_name"], results_df[metric_column])
    plt.title(title)
    plt.xlabel("Model")
    plt.ylabel(metric_column.replace("_", " ").upper())
    plt.xticks(rotation=20)
    plt.tight_layout()

    output_path = OUTPUTS_CHARTS_DIR / filename
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    return output_path


def plot_regression_metric_comparison(
    results_df: pd.DataFrame,
    metric_column: str,
    filename: str,
    title: str,
) -> Path:
    """
    Plot a regression metric comparison chart.

    Args:
        results_df: Regression results DataFrame.
        metric_column: Metric column to plot.
        filename: Output filename.
        title: Chart title.

    Returns:
        Path: Saved chart path.
    """
    plt.figure(figsize=(8, 5))
    plt.bar(results_df["model_name"], results_df[metric_column])
    plt.title(title)
    plt.xlabel("Model")
    plt.ylabel(metric_column.replace("_", " ").upper())
    plt.xticks(rotation=20)
    plt.tight_layout()

    output_path = OUTPUTS_CHARTS_DIR / filename
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    return output_path


def summarize_modeling_outputs(saved_paths: list[Path]) -> None:
    """
    Print a summary of saved modeling outputs.

    Args:
        saved_paths: List of saved output paths.
    """
    print("Refined baseline modeling completed successfully.")
    print("\nSaved files:")

    for path in saved_paths:
        print(f"- {path}")


def main() -> None:
    """
    Run the refined baseline modeling pipeline.
    """
    create_output_directories()

    features_df, conversion_df, visit_df, spend_df = load_modeling_inputs()
    X, _ = prepare_feature_matrix(features_df)

    y_conversion = prepare_target_series(conversion_df, "conversion")
    y_visit = prepare_target_series(visit_df, "visit")
    y_spend = prepare_target_series(spend_df, "spend")

    conversion_results = evaluate_classification_models(
        X=X,
        y=y_conversion,
        target_name="conversion",
    )

    visit_results = evaluate_classification_models(
        X=X,
        y=y_visit,
        target_name="visit",
    )

    spend_results = evaluate_regression_models(
        X=X,
        y=y_spend,
        target_name="spend",
    )

    saved_paths: list[Path] = []

    saved_paths.append(
        save_dataframe(
            conversion_results,
            OUTPUTS_REPORTS_DIR / "modeling_classification_conversion_metrics.csv",
        )
    )
    saved_paths.append(
        save_dataframe(
            visit_results,
            OUTPUTS_REPORTS_DIR / "modeling_classification_visit_metrics.csv",
        )
    )
    saved_paths.append(
        save_dataframe(
            spend_results,
            OUTPUTS_REPORTS_DIR / "modeling_regression_spend_metrics.csv",
        )
    )

    saved_paths.append(
        plot_classification_metric_comparison(
            results_df=conversion_results,
            metric_column="pr_auc",
            filename="conversion_model_pr_auc_comparison.png",
            title="Conversion Model PR-AUC Comparison",
        )
    )
    saved_paths.append(
        plot_classification_metric_comparison(
            results_df=visit_results,
            metric_column="pr_auc",
            filename="visit_model_pr_auc_comparison.png",
            title="Visit Model PR-AUC Comparison",
        )
    )
    saved_paths.append(
        plot_regression_metric_comparison(
            results_df=spend_results,
            metric_column="rmse",
            filename="spend_model_rmse_comparison.png",
            title="Spend Model RMSE Comparison",
        )
    )

    summarize_modeling_outputs(saved_paths)


if __name__ == "__main__":
    main()