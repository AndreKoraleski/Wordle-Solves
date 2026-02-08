from collections import Counter
from logging import getLogger
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from solver.statistics.aggregator import calculate_failure_entropy
from solver.statistics.models import BenchmarkBatch, PerformanceMetrics

logger = getLogger(__name__)

# Global visualization settings
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["font.size"] = 10


def plot_guess_distribution_comparison(
    batches: List[BenchmarkBatch],
    metrics_list: List[PerformanceMetrics],
    output_path: Path,
) -> None:
    """
    Create a grouped bar chart comparing guess distributions across strategies.

    Args:
        batches (List[BenchmarkBatch]): List of benchmark batches to compare.
        metrics_list (List[PerformanceMetrics]): Corresponding metrics for each batch.
        output_path (Path): Path where the plot image will be saved.
    """
    figure, axis = plt.subplots(figsize=(12, 6))

    # Collect all possible guess counts across all strategies
    all_guess_counts = set()
    for metrics in metrics_list:
        all_guess_counts.update(metrics.guess_distribution.keys())

    guess_counts = sorted(all_guess_counts)
    x_positions = np.arange(len(guess_counts))
    bar_width = 0.8 / len(batches)  # Dynamic width based on number of strategies

    # Plot bars for each strategy
    for index, (batch, metrics) in enumerate(zip(batches, metrics_list)):
        frequencies = [
            metrics.guess_distribution.get(guess_count, 0)
            for guess_count in guess_counts
        ]
        offset = (index - len(batches) / 2) * bar_width + bar_width / 2
        axis.bar(
            x_positions + offset,
            frequencies,
            bar_width,
            label=f"{batch.strategy_name}",
            alpha=0.8,
        )

    axis.set_xlabel("Number of Guesses", fontweight="bold")
    axis.set_ylabel("Frequency", fontweight="bold")
    axis.set_title(
        "Guess Distribution Comparison Across Strategies",
        fontsize=14,
        fontweight="bold",
    )
    axis.set_xticks(x_positions)
    axis.set_xticklabels(guess_counts)
    axis.legend(title="Strategy", frameon=True)
    axis.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()

    logger.info(f"Guess distribution comparison saved to {output_path}")


def plot_failure_mode_heatmap(
    metrics: PerformanceMetrics,
    strategy_name: str,
    output_path: Path,
) -> None:
    """
    Create a letter frequency heatmap for failed words to identify common patterns.

    Args:
        metrics (PerformanceMetrics): Performance metrics containing failed words.
        strategy_name (str): Name of the strategy for plot title.
        output_path (Path): Path where the plot image will be saved.
    """
    if not metrics.failed_words:
        logger.info(f"No failures to visualize for {strategy_name}")
        return

    # Create position-based letter frequency matrix
    word_length = 5
    letter_frequencies = {position: Counter() for position in range(word_length)}

    for word in metrics.failed_words:
        word = word.upper()
        for position, letter in enumerate(word[:word_length]):
            letter_frequencies[position][letter] += 1

    # Convert to DataFrame for heatmap
    all_letters = sorted(
        set(
            letter
            for position_counter in letter_frequencies.values()
            for letter in position_counter
        )
    )
    frequency_matrix = []
    for letter in all_letters:
        row = [
            letter_frequencies[position].get(letter, 0)
            for position in range(word_length)
        ]
        frequency_matrix.append(row)

    dataframe = pd.DataFrame(
        frequency_matrix,
        index=all_letters,
        columns=[f"Position {i + 1}" for i in range(word_length)],
    )

    # Create heatmap
    figure, axis = plt.subplots(figsize=(8, 10))
    sns.heatmap(
        dataframe,
        annot=True,
        fmt="d",
        cmap="YlOrRd",
        cbar_kws={"label": "Frequency"},
        ax=axis,
    )
    axis.set_title(
        f"Letter Position Heatmap for Failed Words\n{strategy_name}",
        fontsize=12,
        fontweight="bold",
    )
    axis.set_xlabel("Letter Position", fontweight="bold")
    axis.set_ylabel("Letter", fontweight="bold")

    # Add entropy score as subtitle
    entropy_score = calculate_failure_entropy(metrics.failed_words)
    axis.text(
        0.5,
        -0.15,
        f"Failure Entropy: {entropy_score:.3f} bits",
        transform=axis.transAxes,
        horizontalalignment="center",
        verticalalignment="top",
        fontsize=10,
        style="italic",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
    )

    plt.tight_layout()
    figure.savefig(output_path, bbox_inches="tight")
    plt.close()

    logger.info(f"Failure mode heatmap saved to {output_path}")


def plot_cumulative_winrate(
    batch: BenchmarkBatch,
    output_path: Path,
) -> None:
    """
    Plot running win rate to visualize convergence and volatility over time.

    Args:
        batch (BenchmarkBatch): Benchmark batch containing sequential game results.
        output_path (Path): Path where the plot image will be saved.
    """
    games_list = batch.games
    if not games_list:
        return

    # Calculate cumulative win rate at each game
    cumulative_wins = 0
    win_rate_history = []

    for index, game in enumerate(games_list, start=1):
        if game.won:
            cumulative_wins += 1
        win_rate_history.append((cumulative_wins / index) * 100)

    figure, axis = plt.subplots(figsize=(12, 6))
    axis.plot(range(1, len(games_list) + 1), win_rate_history, linewidth=1.5, alpha=0.8)

    # Add final win rate as horizontal reference line
    final_win_rate = win_rate_history[-1]
    axis.axhline(
        final_win_rate,
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"Final: {final_win_rate:.2f}%",
    )

    axis.set_xlabel("Game Number", fontweight="bold")
    axis.set_ylabel("Cumulative Win Rate (%)", fontweight="bold")
    axis.set_title(
        f"Win Rate Convergence: {batch.strategy_name}\n{batch.oracle_name}",
        fontsize=14,
        fontweight="bold",
    )
    axis.legend(frameon=True)
    axis.grid(alpha=0.3)
    axis.set_ylim([0, 105])

    plt.tight_layout()
    figure.savefig(output_path, bbox_inches="tight")
    plt.close()

    logger.info(f"Cumulative win rate plot saved to {output_path}")


def plot_batch(
    batch: BenchmarkBatch, metrics: PerformanceMetrics, output_directory: Path
) -> None:
    """
    Generate all standard visualizations for a single benchmark batch.

    Args:
        batch (BenchmarkBatch): Benchmark batch to visualize.
        metrics (PerformanceMetrics): Pre-computed performance metrics.
        output_directory (Path): Directory where plots will be saved.
    """
    output_directory.mkdir(parents=True, exist_ok=True)
    plot_cumulative_winrate(batch, output_directory / "convergence.png")

    if metrics.failed_words:
        plot_failure_mode_heatmap(
            metrics, batch.strategy_name, output_directory / "failure_heatmap.png"
        )


def plot_batch_comparison(
    batches: List[BenchmarkBatch],
    metrics_list: List[PerformanceMetrics],
    output_directory: Path,
) -> None:
    """
    Generate comparison visualizations across multiple batches.

    Args:
        batches (List[BenchmarkBatch]): List of benchmark batches to compare.
        metrics_list (List[PerformanceMetrics]): Corresponding metrics for each batch.
        output_directory (Path): Directory where comparison plots will be saved.
    """
    output_directory.mkdir(parents=True, exist_ok=True)
    plot_guess_distribution_comparison(
        batches,
        metrics_list,
        output_directory / "guess_distribution_comparison.png",
    )
