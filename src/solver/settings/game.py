from pydantic import BaseModel, ConfigDict, Field


class GameSettings(BaseModel):
    """
    Settings related to Wordle game configuration.

    Attributes:
        max_turns (int): Maximum number of guesses allowed per game.
    """

    model_config = ConfigDict(extra="ignore")

    max_turns: int = Field(
        default=6,
        gt=0,
        description="Maximum number of guesses allowed per game.",
    )
