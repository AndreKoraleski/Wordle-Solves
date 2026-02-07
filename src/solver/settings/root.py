from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from solver.settings.game import GameSettings
from solver.settings.logging import LoggingSettings
from solver.settings.path import PathSettings


class Settings(BaseSettings):
    """
    Settings class that provides configuration values using defaults,
    environment variables, or a `.env` file.

    Environment variables and `.env` entries must follow the format:
        WORDLE_<MODULE>__<SETTING>

    Nested settings can be defined by adding additional `__` separators.

    New settings should be added to this class as they become necessary.

    Attributes:
        game (GameSettings): Configuration related to the Wordle game.
        logging (LoggingSettings): Configuration related to logging.
        path (PathSettings): Configuration related to path handling.
    """

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_prefix="WORDLE_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,  # If the variable is empty, it's treated as not set
        validate_assignment=True,
    )

    game: GameSettings = Field(
        default=GameSettings, description="Configuration related to the Wordle game."
    )
    logging: LoggingSettings = Field(
        default=LoggingSettings,
        description="Configuration related to logging.",
    )

    path: PathSettings = Field(
        default=PathSettings, description="Configuration related to path handling."
    )
