from collections import Counter
from math import log2
from statistics import mean, median, stdev
from typing import Dict, List

from solver.statistics.models import PerformanceMetrics, BenchmarkBatch


def calculate_failure_entropy(failed_words: List[str]) -> float:
    """
    Calculate the Shannon entropy of letter frequencies in failed words.

    Higher entropy indicates failures are spread across diverse letter patterns.
    Lower entropy suggests failures cluster around specific letter combinations.

    Args:
        failed_words (List[str]): List of words that resulted in losses.

    Returns:
        float: Entropy value in bits. Returns 0.0 if no failed words.
    """
    if not failed_words:
        return 0.0

    # Concatenate all failed words and count letter frequencies
    all_letters = "".join(failed_words).lower()
    letter_counts = Counter(all_letters)
    total_letters = len(all_letters)

    # Calculate Shannon entropy
    entropy = 0.0
    for count in letter_counts.values():
        probability = count / total_letters
        entropy -= probability * log2(probability)

    return round(entropy, 3)


def compute_metrics(batch: BenchmarkBatch) -> PerformanceMetrics:
    """
    Analyze a simulation batch and calculate performance statistics.

    Args:
        batch (BenchmarkBatch): The batch of game results to analyze.

    Returns:
        PerformanceMetrics: A populated metrics object containing the analysis.
    """
    games = batch.games
    total = len(games)

    # Handle empty batch edge case
    if total == 0:
        return PerformanceMetrics(
            total_games=0,
            win_rate=0.0,
            average_duration_ms=0.0,
            solve_efficiency_mean=0.0,
            solve_efficiency_median=0.0,
            solve_efficiency_standard_deviation=0.0,
            guess_distribution={},
            worst_case_guesses=0,
            failed_words=[],
            failure_entropy=0.0,
        )

    # 1. Filter results
    wins = [game for game in games if game.won]
    losses = [game for game in games if not game.won]

    # 2. Calculate Efficiency (Wins Only)
    guess_counts = [game.number_of_guesses for game in wins]

    if guess_counts:
        mean_guesses = mean(guess_counts)
        median_guesses = median(guess_counts)
        max_guesses = max(guess_counts)

        # Standard deviation requires at least two data points
        if len(guess_counts) > 1:
            standard_deviation_guesses = stdev(guess_counts)
        else:
            standard_deviation_guesses = 0.0
    else:
        # No wins
        mean_guesses = 0.0
        median_guesses = 0.0
        standard_deviation_guesses = 0.0
        max_guesses = 0

    # 3. Calculate Distribution
    distribution: Dict[int, int] = {}
    for count in guess_counts:
        distribution[count] = distribution.get(count, 0) + 1

    # Sort distribution by keys (1 guess, 2 guesses, etc.)
    sorted_dist = dict(sorted(distribution.items()))

    # 4. Calculate Time
    # Convert nanoseconds to milliseconds for ease of interpretation
    average_time_ms = mean([game.duration_ns for game in games]) / 1_000_000

    # 5. Calculate Failure Entropy
    failed_word_list = [game.answer for game in losses]
    entropy = calculate_failure_entropy(failed_word_list)

    return PerformanceMetrics(
        total_games=total,
        win_rate=(len(wins) / total) * 100,
        average_duration_ms=round(average_time_ms, 2),
        solve_efficiency_mean=round(mean_guesses, 3),
        solve_efficiency_median=round(median_guesses, 3),
        solve_efficiency_standard_deviation=round(standard_deviation_guesses, 3),
        guess_distribution=sorted_dist,
        worst_case_guesses=max_guesses,
        failed_words=failed_word_list,
        failure_entropy=entropy,
    )
