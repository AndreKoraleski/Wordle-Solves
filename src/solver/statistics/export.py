from collections import defaultdict
from csv import writer as csv_writer
from json import dump
from logging import getLogger
from pathlib import Path
from statistics import mean, median, stdev
from typing import Any, List

from solver.settings.path import PathSettings
from solver.statistics.aggregator import compute_metrics
from solver.statistics.models import BenchmarkBatch, PerformanceMetrics
from solver.statistics.visualizer import plot_batch, plot_batch_comparison

logger = getLogger(__name__)


def save_benchmark_results(batches: List[BenchmarkBatch], paths: PathSettings) -> None:
    """
    Save benchmark results to disk in multiple formats.

    Results are organized by oracle and solver:
    - Individual runs: statistics/runs/{oracle_name}/{solver_name}/{timestamp}/
    - Comparisons: statistics/comparisons/

    Args:
        batches (List[BenchmarkBatch]): List of benchmark batches to export.
        paths (PathSettings): Global path settings object containing path configurations.
    """
    if not batches:
        return

    # Use the timestamp from the first batch for naming consistency
    timestamp = batches[0].timestamp if batches else "unknown"

    # Pre-calculate metrics for all batches
    results = [(batch, compute_metrics(batch)) for batch in batches]

    _create_gitignore(paths.statistics_folder)

    # Save individual batch results in organized folders
    for batch, stats in results:
        # Create oracle/solver/timestamp folder structure
        batch_output_directory = (
            paths.statistics_runs_folder
            / _sanitize_name(batch.oracle_name)
            / _sanitize_name(batch.strategy_name)
            / timestamp
        )
        batch_output_directory.mkdir(parents=True, exist_ok=True)

        # Save individual batch files
        _save_batch_summary(batch, stats, batch_output_directory)
        _save_batch_csv(batch, batch_output_directory)
        _save_batch_json(batch, stats, batch_output_directory)
        _save_performance_stats(batch, batch_output_directory)

        # Generate visualizations for this batch
        plot_batch(batch, stats, batch_output_directory)

    # Save comparison files if multiple batches
    if len(results) > 1:
        comparison_directory = paths.statistics_comparisons_folder
        comparison_directory.mkdir(parents=True, exist_ok=True)
        _save_comparison_summary(results, comparison_directory, timestamp)
        _save_comparison_json(results, comparison_directory, timestamp)

        # Generate comparison visualizations
        batches_list = [batch for batch, _ in results]
        metrics_list = [stats for _, stats in results]
        plot_batch_comparison(batches_list, metrics_list, comparison_directory)


def _sanitize_name(name: str) -> str:
    """
    Sanitize a name for use in file/folder names.

    Args:
        name: The name to sanitize.

    Returns:
        Sanitized name with only alphanumeric characters and underscores.
    """
    return "".join(
        character if character.isalnum() or character in ("-", "_") else "_"
        for character in name
    )


def _create_gitignore(directory: Path) -> None:
    """
    Create a .gitignore file to prevent statistics from being committed to git.

    Args:
        directory (Path): Directory in which to create the .gitignore file.
    """
    directory.mkdir(parents=True, exist_ok=True)
    gitignore_path = directory / ".gitignore"
    with open(gitignore_path, "w", encoding="utf-8") as file:
        file.write("# Automatically created by export script\n")
        file.write("*\n")


def _save_batch_summary(
    batch: BenchmarkBatch, stats: PerformanceMetrics, output_directory: Path
) -> None:
    """
    Generate a human-readable text report for a single batch.

    Args:
        batch (BenchmarkBatch): Benchmark batch to export.
        stats (PerformanceMetrics): Computed performance metrics.
        output_directory (Path): Directory to save the summary.
    """
    summary_path = output_directory / "summary.txt"

    with open(summary_path, "w", encoding="utf-8") as file:
        file.write("=" * 80 + "\n")
        file.write("WORDLE SOLVER BENCHMARK RESULTS\n")
        file.write("=" * 80 + "\n\n")
        file.write(f"Oracle: {batch.oracle_name}\n")
        file.write(f"Strategy: {batch.strategy_name}\n")
        file.write(f"Timestamp: {batch.timestamp}\n\n")

        file.write("-" * 80 + "\n")
        file.write("PERFORMANCE SUMMARY\n")
        file.write("-" * 80 + "\n")
        file.write(f"Total games: {stats.total_games}\n")
        file.write(f"Win rate: {stats.win_rate:.2f}%\n")
        file.write(f"Avg duration: {stats.average_duration_ms:.2f} ms\n")
        file.write("\nEfficiency (Wins only):\n")
        file.write(f"  Mean guesses:   {stats.solve_efficiency_mean:.3f}\n")
        file.write(f"  Median guesses: {stats.solve_efficiency_median:.1f}\n")
        file.write(
            f"  Std Dev:        {stats.solve_efficiency_standard_deviation:.3f}\n"
        )
        file.write(f"  Worst case:     {stats.worst_case_guesses} guesses\n")

        file.write("\nGuess Distribution:\n")
        for num_guesses, count in stats.guess_distribution.items():
            pct = (count / stats.total_games * 100) if stats.total_games else 0
            file.write(f"  {num_guesses}: {count} ({pct:.1f}%)\n")

        if stats.failed_words:
            file.write(f"\nFailed Words ({len(stats.failed_words)}):  \n")
            for word in stats.failed_words:
                file.write(f"  {word}\n")

    logger.info(f"Summary saved to {summary_path}")


def _save_batch_csv(batch: BenchmarkBatch, output_directory: Path) -> None:
    """
    Generate a detailed CSV file containing raw game data for a single batch.

    Args:
        batch (BenchmarkBatch): Benchmark batch to export.
        output_directory (Path): Directory to save the CSV.
    """
    csv_path = output_directory / "results.csv"

    # Find maximum number of guesses across all games
    max_guesses = max((len(game.guesses) for game in batch.games), default=0)

    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv_writer(file)

        # Build dynamic header with individual guess columns
        header = ["Answer", "Won", "Number of Guesses", "Duration (ms)", "Seed"]
        header.extend([f"Guess {i + 1}" for i in range(max_guesses)])
        writer.writerow(header)

        # Write rows with individual guess columns
        for game in batch.games:
            row = [
                game.answer,
                game.won,
                len(game.guesses),
                round(game.duration_ns / 1_000_000, 2),
                game.random_seed if game.random_seed is not None else "",
            ]
            # Add individual guesses, padding with empty strings
            row.extend(game.guesses)
            row.extend([""] * (max_guesses - len(game.guesses)))
            writer.writerow(row)

    logger.info(f"Detailed results saved to {csv_path}")


def _save_performance_stats(batch: BenchmarkBatch, output_directory: Path) -> None:
    """
    Generate a CSV file with performance statistics grouped by guess count.

    Args:
        batch: Benchmark batch to analyze.
        output_directory: Directory to save the performance stats CSV.
    """
    performance_path = output_directory / "performance_by_guesses.csv"

    # Group games by guess count and calculate statistics
    stats_by_guess = defaultdict(list)

    for game in batch.games:
        guess_count = len(game.guesses)
        duration_ms = game.duration_ns / 1_000_000
        stats_by_guess[guess_count].append(
            {"duration_ms": duration_ms, "won": game.won}
        )

    with open(performance_path, "w", newline="", encoding="utf-8") as file:
        writer = csv_writer(file)
        writer.writerow(
            [
                "Guesses",
                "Total Games",
                "Wins",
                "Losses",
                "Mean Duration (ms)",
                "Median Duration (ms)",
                "Std Dev Duration (ms)",
                "Min Duration (ms)",
                "Max Duration (ms)",
            ]
        )

        for guess_count in sorted(stats_by_guess.keys()):
            games_data = stats_by_guess[guess_count]
            durations = [g["duration_ms"] for g in games_data]
            wins = sum(1 for g in games_data if g["won"])
            losses = len(games_data) - wins

            mean_duration = mean(durations)
            median_duration = median(durations)
            std_duration = stdev(durations) if len(durations) > 1 else 0.0
            min_duration = min(durations)
            max_duration = max(durations)

            writer.writerow(
                [
                    guess_count,
                    len(games_data),
                    wins,
                    losses,
                    f"{mean_duration:.2f}",
                    f"{median_duration:.2f}",
                    f"{std_duration:.2f}",
                    f"{min_duration:.2f}",
                    f"{max_duration:.2f}",
                ]
            )

    logger.info(f"Performance statistics saved to {performance_path}")


def _save_batch_json(
    batch: BenchmarkBatch, stats: PerformanceMetrics, output_directory: Path
) -> None:
    """
    Generate a machine-readable JSON file for a single batch.

    Args:
        batch (BenchmarkBatch): Benchmark batch to export.
        stats (PerformanceMetrics): Computed performance metrics.
        output_directory (Path): Directory to save the JSON.
    """
    json_path = output_directory / "metrics.json"

    def json_serializer(obj: Any) -> Any:
        """Custom JSON serializer that handles Path objects with forward slashes."""
        if isinstance(obj, Path):
            return obj.as_posix()
        return str(obj)

    data = {
        "oracle": batch.oracle_name,
        "strategy": batch.strategy_name,
        "timestamp": batch.timestamp,
        "settings": batch.settings,
        "metrics": stats.model_dump(),
    }

    with open(json_path, "w", encoding="utf-8") as file:
        dump(data, file, indent=2, default=json_serializer)

    logger.info(f"Metrics JSON saved to {json_path}")


def _save_comparison_summary(
    results: List[tuple[BenchmarkBatch, PerformanceMetrics]],
    output_directory: Path,
    timestamp: str,
) -> None:
    """
    Generate a human-readable text report.

    Args:
        results (List[tuple[BenchmarkBatch, PerformanceMetrics]]): List of tuples containing benchmark batches and their metrics.
        output_directory (Path): Directory to save the summary.
        timestamp (str): Timestamp string for filenames.
    """
    summary_path = output_directory / f"summary_{timestamp}.txt"

    with open(summary_path, "w", encoding="utf-8") as file:
        file.write("=" * 80 + "\n")
        file.write("WORDLE SOLVER STRATEGY COMPARISON\n")
        file.write("=" * 80 + "\n\n")
        file.write(f"Timestamp: {timestamp}\n")
        file.write(f"Strategies tested: {len(results)}\n\n")

        # Individual Strategy Details
        for batch, stats in results:
            file.write("-" * 80 + "\n")
            file.write(f"Strategy: {batch.strategy_name}\n")
            file.write("-" * 80 + "\n")
            file.write(f"Total games: {stats.total_games}\n")
            file.write(f"Win rate: {stats.win_rate:.2f}%\n")
            file.write(f"Avg duration: {stats.average_duration_ms:.2f} ms\n")
            file.write("\nEfficiency (Wins only):\n")
            file.write(f"  Mean guesses:   {stats.solve_efficiency_mean:.3f}\n")
            file.write(f"  Median guesses: {stats.solve_efficiency_median:.1f}\n")
            file.write(
                f"  Std Dev:        {stats.solve_efficiency_standard_deviation:.3f}\n"
            )
            file.write(f"  Worst case:     {stats.worst_case_guesses} guesses\n")

            file.write("\nGuess Distribution:\n")
            for num_guesses, count in stats.guess_distribution.items():
                pct = (count / stats.total_games * 100) if stats.total_games else 0
                file.write(f"  {num_guesses}: {count} ({pct:.1f}%)\n")
            file.write("\n")

        # Comparative Table
        file.write("=" * 80 + "\n")
        file.write("COMPARISON SUMMARY\n")
        file.write("=" * 80 + "\n\n")

        header = (
            f"{'Strategy':<35} {'Win Rate':<10} {'Avg Guesses':<12} {'Time (ms)':<10}\n"
        )
        file.write(header)
        file.write("-" * 80 + "\n")

        for batch, stats in results:
            line = (
                f"{batch.strategy_name:<35} "
                f"{stats.win_rate:>6.2f}%   "
                f"{stats.solve_efficiency_mean:>8.3f}    "
                f"{stats.average_duration_ms:>8.2f}\n"
            )
            file.write(line)

    logger.info(f"Comparison summary saved to {summary_path}")


def _save_comparison_json(
    results: List[tuple[BenchmarkBatch, PerformanceMetrics]],
    output_directory: Path,
    timestamp: str,
) -> None:
    """
    Generate a machine-readable JSON summary of the metrics.

    Args:
        results: List of tuples containing benchmark batches and their metrics.
        output_directory: Directory to save the summary.
        timestamp: Timestamp string for filenames.
    """
    json_path = output_directory / f"comparison_{timestamp}.json"

    def json_serializer(object: Any) -> Any:
        """
        Custom JSON serializer that handles Path objects with forward slashes.

        Args:
            object: The object to serialize.

        Returns:
            A JSON-serializable representation of the object.
        """
        if isinstance(object, Path):
            return object.as_posix()
        return str(object)

    data = {"timestamp": timestamp, "strategies": []}

    for batch, stats in results:
        strategy_data = {
            "name": batch.strategy_name,
            "settings": batch.settings,
            "metrics": stats.model_dump(),
        }
        data["strategies"].append(strategy_data)

    with open(json_path, "w", encoding="utf-8") as file:
        dump(data, file, indent=2, default=json_serializer)

    logger.info(f"Comparison JSON saved to {json_path}")
