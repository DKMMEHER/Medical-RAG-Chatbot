"""
Visualization Script for RAG Evaluation Results

This script creates visualizations for the RAG evaluation metrics:
- Bar charts for average metrics
- Heatmap for individual question performance
- Distribution plots for each metric
"""

import os
import sys
import logging
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/visualize.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# Constants
RESULTS_DIR = "evaluation/results"
PLOTS_DIR = "evaluation/plots"

# Set style
sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (12, 8)


def find_latest_results(results_dir: str) -> str:
    """
    Find the latest evaluation metrics CSV file.

    Args:
        results_dir: Directory containing results

    Returns:
        str: Path to latest CSV file
    """
    try:
        csv_files = list(Path(results_dir).glob("evaluation_metrics_*.csv"))

        if not csv_files:
            raise FileNotFoundError(f"No evaluation results found in {results_dir}")

        # Sort by modification time and get the latest
        latest_file = max(csv_files, key=lambda p: p.stat().st_mtime)
        logger.info(f"Found latest results: {latest_file}")
        return str(latest_file)

    except Exception as e:
        logger.error(f"Error finding results: {str(e)}")
        raise


def load_results(csv_path: str) -> pd.DataFrame:
    """
    Load evaluation results from CSV.

    Args:
        csv_path: Path to CSV file

    Returns:
        pd.DataFrame: Results dataframe
    """
    try:
        logger.info(f"Loading results from {csv_path}")
        df = pd.read_csv(csv_path)
        logger.info(f"Loaded {len(df)} records")
        return df

    except Exception as e:
        logger.error(f"Error loading results: {str(e)}")
        raise


def create_average_metrics_plot(df: pd.DataFrame, output_dir: str):
    """
    Create bar chart of average metrics.

    Args:
        df: Results dataframe
        output_dir: Directory to save plot
    """
    try:
        logger.info("Creating average metrics plot...")

        # Calculate average scores
        metrics = [
            "faithfulness",
            "answer_relevancy",
            "context_precision",
            "context_recall",
        ]
        avg_scores = {
            metric: df[metric].mean() for metric in metrics if metric in df.columns
        }

        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))

        colors = ["#2ecc71", "#3498db", "#9b59b6", "#e74c3c"]
        bars = ax.bar(
            range(len(avg_scores)), list(avg_scores.values()), color=colors, alpha=0.8
        )

        # Customize plot
        ax.set_xlabel("Metrics", fontsize=12, fontweight="bold")
        ax.set_ylabel("Score", fontsize=12, fontweight="bold")
        ax.set_title(
            "RAG Evaluation - Average Metrics", fontsize=14, fontweight="bold", pad=20
        )
        ax.set_xticks(range(len(avg_scores)))
        ax.set_xticklabels(
            [m.replace("_", " ").title() for m in avg_scores.keys()],
            rotation=45,
            ha="right",
        )
        ax.set_ylim(0, 1.0)
        ax.grid(axis="y", alpha=0.3)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{height:.3f}",
                ha="center",
                va="bottom",
                fontweight="bold",
            )

        plt.tight_layout()

        # Save plot
        output_path = os.path.join(output_dir, "average_metrics.png")
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        logger.info(f"Saved average metrics plot to {output_path}")
        plt.close()

    except Exception as e:
        logger.error(f"Error creating average metrics plot: {str(e)}")
        raise


def create_metrics_distribution_plot(df: pd.DataFrame, output_dir: str):
    """
    Create distribution plots for each metric.

    Args:
        df: Results dataframe
        output_dir: Directory to save plot
    """
    try:
        logger.info("Creating metrics distribution plot...")

        metrics = [
            "faithfulness",
            "answer_relevancy",
            "context_precision",
            "context_recall",
        ]
        available_metrics = [m for m in metrics if m in df.columns]

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        axes = axes.flatten()

        colors = ["#2ecc71", "#3498db", "#9b59b6", "#e74c3c"]

        for idx, metric in enumerate(available_metrics):
            ax = axes[idx]

            # Create histogram with KDE
            ax.hist(
                df[metric], bins=10, alpha=0.6, color=colors[idx], edgecolor="black"
            )

            # Add KDE line
            df[metric].plot(
                kind="kde", ax=ax, color=colors[idx], linewidth=2, secondary_y=True
            )

            # Customize
            ax.set_xlabel("Score", fontsize=10, fontweight="bold")
            ax.set_ylabel("Frequency", fontsize=10, fontweight="bold")
            ax.set_title(
                metric.replace("_", " ").title(), fontsize=12, fontweight="bold"
            )
            ax.grid(alpha=0.3)

            # Add mean line
            mean_val = df[metric].mean()
            ax.axvline(
                mean_val,
                color="red",
                linestyle="--",
                linewidth=2,
                label=f"Mean: {mean_val:.3f}",
            )
            ax.legend()

        plt.suptitle(
            "Distribution of RAG Metrics", fontsize=16, fontweight="bold", y=1.00
        )
        plt.tight_layout()

        # Save plot
        output_path = os.path.join(output_dir, "metrics_distribution.png")
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        logger.info(f"Saved distribution plot to {output_path}")
        plt.close()

    except Exception as e:
        logger.error(f"Error creating distribution plot: {str(e)}")
        raise


def create_heatmap(df: pd.DataFrame, output_dir: str):
    """
    Create heatmap of metrics for each question.

    Args:
        df: Results dataframe
        output_dir: Directory to save plot
    """
    try:
        logger.info("Creating heatmap...")

        metrics = [
            "faithfulness",
            "answer_relevancy",
            "context_precision",
            "context_recall",
        ]
        available_metrics = [m for m in metrics if m in df.columns]

        # Prepare data for heatmap
        heatmap_data = df[available_metrics].T

        # Create plot
        fig, ax = plt.subplots(figsize=(14, 6))

        sns.heatmap(
            heatmap_data,
            annot=True,
            fmt=".3f",
            cmap="RdYlGn",
            cbar_kws={"label": "Score"},
            ax=ax,
            vmin=0,
            vmax=1,
        )

        # Customize
        ax.set_xlabel("Question Index", fontsize=12, fontweight="bold")
        ax.set_ylabel("Metrics", fontsize=12, fontweight="bold")
        ax.set_title(
            "RAG Metrics Heatmap - Per Question Performance",
            fontsize=14,
            fontweight="bold",
            pad=20,
        )
        ax.set_yticklabels(
            [m.replace("_", " ").title() for m in available_metrics], rotation=0
        )

        plt.tight_layout()

        # Save plot
        output_path = os.path.join(output_dir, "metrics_heatmap.png")
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        logger.info(f"Saved heatmap to {output_path}")
        plt.close()

    except Exception as e:
        logger.error(f"Error creating heatmap: {str(e)}")
        raise


def create_comparison_plot(df: pd.DataFrame, output_dir: str):
    """
    Create comparison plot showing all metrics for each question.

    Args:
        df: Results dataframe
        output_dir: Directory to save plot
    """
    try:
        logger.info("Creating comparison plot...")

        metrics = [
            "faithfulness",
            "answer_relevancy",
            "context_precision",
            "context_recall",
        ]
        available_metrics = [m for m in metrics if m in df.columns]

        # Create plot
        fig, ax = plt.subplots(figsize=(14, 8))

        x = range(len(df))
        width = 0.2
        colors = ["#2ecc71", "#3498db", "#9b59b6", "#e74c3c"]

        for idx, metric in enumerate(available_metrics):
            offset = width * (idx - len(available_metrics) / 2 + 0.5)
            ax.bar(
                [i + offset for i in x],
                df[metric],
                width,
                label=metric.replace("_", " ").title(),
                color=colors[idx],
                alpha=0.8,
            )

        # Customize
        ax.set_xlabel("Question Index", fontsize=12, fontweight="bold")
        ax.set_ylabel("Score", fontsize=12, fontweight="bold")
        ax.set_title(
            "RAG Metrics Comparison - All Questions",
            fontsize=14,
            fontweight="bold",
            pad=20,
        )
        ax.set_xticks(x)
        ax.set_xticklabels([f"Q{i + 1}" for i in x])
        ax.set_ylim(0, 1.1)
        ax.legend(loc="upper right", framealpha=0.9)
        ax.grid(axis="y", alpha=0.3)

        plt.tight_layout()

        # Save plot
        output_path = os.path.join(output_dir, "metrics_comparison.png")
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        logger.info(f"Saved comparison plot to {output_path}")
        plt.close()

    except Exception as e:
        logger.error(f"Error creating comparison plot: {str(e)}")
        raise


def main():
    """Main visualization function"""

    print("=" * 60)
    print("RAG EVALUATION - RESULTS VISUALIZATION")
    print("=" * 60)
    print()

    try:
        # Create plots directory
        Path(PLOTS_DIR).mkdir(parents=True, exist_ok=True)

        # Step 1: Find latest results
        print("📁 Step 1: Finding latest evaluation results...")
        csv_path = find_latest_results(RESULTS_DIR)
        print(f"✅ Found: {csv_path}")
        print()

        # Step 2: Load results
        print("📊 Step 2: Loading results...")
        df = load_results(csv_path)
        print(f"✅ Loaded {len(df)} records")
        print()

        # Step 3: Create visualizations
        print("🎨 Step 3: Creating visualizations...")

        print("  - Creating average metrics plot...")
        create_average_metrics_plot(df, PLOTS_DIR)

        print("  - Creating distribution plots...")
        create_metrics_distribution_plot(df, PLOTS_DIR)

        print("  - Creating heatmap...")
        create_heatmap(df, PLOTS_DIR)

        print("  - Creating comparison plot...")
        create_comparison_plot(df, PLOTS_DIR)

        print("✅ All visualizations created")
        print()

        # Summary
        print("=" * 60)
        print("✅ SUCCESS! Visualizations created")
        print("=" * 60)
        print()
        print(f"📁 Plots saved to: {PLOTS_DIR}")
        print()
        print("Generated plots:")
        print("  1. average_metrics.png - Bar chart of average scores")
        print("  2. metrics_distribution.png - Distribution of each metric")
        print("  3. metrics_heatmap.png - Heatmap of per-question performance")
        print("  4. metrics_comparison.png - Side-by-side comparison")
        print()

        logger.info("Visualization completed successfully")
        return 0

    except Exception as e:
        print()
        print("=" * 60)
        print("❌ ERROR")
        print("=" * 60)
        print(f"Error: {str(e)}")
        print()
        print("💡 Suggestions:")
        print("  - Ensure evaluation has been run (run evaluate_rag.py)")
        print("  - Check that results directory exists")
        print()
        logger.error(f"Visualization failed: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
