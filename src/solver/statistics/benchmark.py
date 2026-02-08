from datetime import datetime
from logging import getLogger
from math import ceil
from statistics import NormalDist
from typing import Any, Dict, List

from solver.game.engine import GameEngine
from solver.game.result import GameResult
from solver.oracle.base import Oracle
from solver.settings.game import GameSettings
from solver.settings.path import PathSettings
from solver.statistics.models import BenchmarkBatch
from solver.strategy.base import Solver


logger = getLogger(__name__)


def calculate_sample_size(
    confidence_level: float = 0.95,
    margin_of_error: float = 0.01,
    estimated_proportion: float = 0.5,
) -> int:
    """
    Calculate the required sample size for a proportion using the Z-score formula.

    Formula: n = (Z^2 * p * (1-p)) / E^2

    Where:
        Z = Z-score for confidence level
        p = estimated proportion (default 0.5 for maximum variance)
        E = margin of error

    Args:
        confidence_level: Desired confidence level between 0 and 1 (e.g., 0.95 for 95%).
        margin_of_error: Acceptable margin of error (e.g., 0.01 for ±1%).
        estimated_proportion: Expected proportion (default 0.5 for conservative estimate).

    Returns:
        int: Required sample size (number of games).

    Raises:
        ValueError: If confidence_level is not between 0 and 1.
    """
    if not 0 < confidence_level < 1:
        raise ValueError(
            f"Confidence level must be between 0 and 1, got: {confidence_level}"
        )

    # Calculate Z-score dynamically
    z = NormalDist().inv_cdf((1 + confidence_level) / 2)

    p = estimated_proportion
    e = margin_of_error

    # Apply formula
    n = (z**2 * p * (1 - p)) / (e**2)

    return ceil(n)


def run_benchmark(
    oracle: Oracle,
    solver: Solver,
    oracle_name: str,
    strategy_name: str,
    game_settings: GameSettings,
    path_settings: PathSettings,
    number_of_games: int | None = None,
    confidence_level: float = 0.95,
    margin_of_error: float = 0.01,
    estimated_proportion: float = 0.5,
    progress_interval: int = 100,
    settings_snapshot: Dict[str, Any] | None = None,
) -> BenchmarkBatch:
    """
    Run a benchmark by executing multiple games with the same Oracle and Solver.

    Args:
        oracle (Oracle): Oracle instance for selecting answer words.
        solver (Solver): Solver instance for generating guesses.
        oracle_name (str): Name of the oracle strategy for reporting.
        strategy_name (str): Name of the solver strategy for reporting.
        game_settings (GameSettings): Configuration for game rules.
        path_settings (PathSettings): Configuration for word list paths.
        number_of_games (int | None): Number of games to simulate. If None, calculated from statistical parameters.
        confidence_level (float): Confidence level for sample size calculation (default 0.95).
        margin_of_error (float): Margin of error for sample size calculation (default 0.01).
        estimated_proportion (float): Expected proportion for sample size calculation (default 0.5).
        progress_interval (int): Log progress every N games (default 100). Set to 0 to disable.
        settings_snapshot (Dict[str, Any] | None): Optional dictionary of settings to store with results.

    Returns:
        BenchmarkBatch: Container with all game results and metadata.
    """
    # Determine sample size
    if number_of_games is None:
        number_of_games = calculate_sample_size(
            confidence_level=confidence_level,
            margin_of_error=margin_of_error,
            estimated_proportion=estimated_proportion,
        )
        logger.info(
            f"Calculated sample size: {number_of_games} games "
            f"({confidence_level * 100:.1f}% confidence, ±{margin_of_error * 100:.1f}%)"
        )

    logger.info(
        f"Starting benchmark: {strategy_name} with {oracle_name} ({number_of_games} games)"
    )

    results: List[GameResult] = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create engine with the provided oracle and solver
    engine = GameEngine(
        settings=game_settings,
        paths=path_settings,
        chooser=oracle,
        solver=solver,
    )

    for index in range(number_of_games):
        # Generate deterministic seed for reproducibility
        seed = index

        # Run game
        result = engine.run(random_seed=seed)
        results.append(result)

        # Progress logging
        if progress_interval > 0 and (index + 1) % progress_interval == 0:
            logger.info(f"Progress: {index + 1}/{number_of_games} games completed")

    logger.info(
        f"Benchmark complete: {strategy_name} - "
        f"{sum(1 for r in results if r.won)}/{number_of_games} wins"
    )

    # Package results into batch
    return BenchmarkBatch(
        oracle_name=oracle_name,
        strategy_name=strategy_name,
        timestamp=timestamp,
        settings=settings_snapshot or {},
        games=results,
    )
