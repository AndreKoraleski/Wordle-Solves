from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class GameResult(BaseModel):
    """
    Atomic record of a single game's execution.

    Attributes:
        answer (str): The hidden answer word for the game.
        won (bool): Whether the game was won.
        guesses (List[str]): List of guesses made in order.
        duration_ns (int): Duration of the game in nanoseconds.
        random_seed (Optional[int]): Optional random seed used for reproducibility.
        number_of_guesses (int): Computed property for the number of guesses made.
    """

    answer: str = Field(..., description="The hidden answer word for the game.")
    won: bool = Field(..., description="Whether the game was won.")
    guesses: List[str] = Field(..., description="List of guesses made in order.")
    duration_ns: int = Field(..., description="Duration of the game in nanoseconds.")
    random_seed: Optional[int] = Field(
        None, description="Optional random seed used for reproducibility."
    )

    @property
    def number_of_guesses(self) -> int:
        return len(self.guesses)

    model_config = ConfigDict(frozen=True, extra="ignore")
