from typing import Any, Dict, List

from pydantic import BaseModel, Field

from solver.game.result import GameResult


class BenchmarkBatch(BaseModel):
    """
    Container for a full benchmark run.

    Attributes:
        oracle_name (str): Name of the oracle strategy used.
        strategy_name (str): Name of the strategy used.
        timestamp (str): ISO formatted timestamp of the run.
        settings (Dict[str, Any]): Snapshot of the game/solver settings used.
        games (List[GameResult]): List of game results.
    """

    oracle_name: str = Field(..., description="Name of the oracle strategy used.")
    strategy_name: str = Field(..., description="Name of the strategy used.")
    timestamp: str = Field(..., description="ISO formatted timestamp of the run.")
    settings: Dict[str, Any] = Field(
        default_factory=dict, description="Snapshot of the game/solver settings used."
    )
    games: List[GameResult] = Field(..., description="List of game results.")

    @property
    def total_games(self) -> int:
        """
        Total number of games in the batch.

        Returns:
            int: The total number of games.
        """
        return len(self.games)


class PerformanceMetrics(BaseModel):
    """
    Aggregated statistics derived from a BenchmarkBatch.

    Attributes:
        total_games (int): Total number of games played.
        win_rate (float): Percentage of games won (0-100).
        average_duration_ms (float): Average game time in milliseconds.
        solve_efficiency_mean (float): Mean guesses for solved games.
        solve_efficiency_median (float): Median guesses for solved games.
        solve_efficiency_standard_deviation (float): Standard deviation of guesses.
        guess_distribution (Dict[int, int]): Count of games solved in N guesses.
        worst_case_guesses (int): Max guesses taken in any winning game.
        failed_words (List[str]): List of answer words that resulted in a loss.
        failure_entropy (float): Shannon entropy of letter frequencies in failed words.
    """

    # --- High Level Stats ---
    total_games: int = Field(..., description="Total games played.")
    win_rate: float = Field(..., description="Percentage of games won (0-100).")
    average_duration_ms: float = Field(
        ..., description="Average game time in milliseconds."
    )

    # --- Efficiency Stats (Wins Only) ---
    solve_efficiency_mean: float = Field(
        ..., description="Mean guesses for solved games."
    )
    solve_efficiency_median: float = Field(
        ..., description="Median guesses for solved games."
    )
    solve_efficiency_standard_deviation: float = Field(
        ..., description="Standard deviation of guesses."
    )

    # --- Distribution & Outliers ---
    guess_distribution: Dict[int, int] = Field(
        ..., description="Count of games solved in N guesses."
    )
    worst_case_guesses: int = Field(
        ..., description="Max guesses taken in any winning game."
    )
    failed_words: List[str] = Field(
        default_factory=list,
        description="List of answer words that resulted in a loss.",
    )
    failure_entropy: float = Field(
        default=0.0,
        description="Shannon entropy of letter frequencies in failed words (bits).",
    )
