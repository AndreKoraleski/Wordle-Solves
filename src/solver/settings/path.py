from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PathSettings(BaseModel):
    """
    Configuration settings related to default data file paths.

    Paths are resolved relative to the repository root unless
    explicitly overridden.

    Attributes:
        data_folder (Path):
            Directory containing data files.

        word_bank_csv (Path):
            Path to the Wordle solution word bank CSV file.

        valid_words_csv (Path):
            Path to the CSV file containing all valid Wordle guesses.
    """

    model_config = ConfigDict(extra="ignore")

    data_folder: Path = Field(
        default=Path("data"), description="Directory containing project data files."
    )

    statistics_folder: Path = Field(
        default=Path("statistics"),
        description="Directory for storing aggregated statistics and summaries.",
    )

    cache_folder: Path = Field(
        default=Path(".cache"), description="Directory for storing cached data."
    )

    word_bank_csv: Path | None = Field(
        default=None, description="Path to the Wordle solution word bank CSV file."
    )

    valid_words_csv: Path | None = Field(
        default=None,
        description="Path to the CSV file containing all valid Wordle guesses.",
    )

    @model_validator(mode="after")
    def set_default_paths(self):
        """
        Populate dependent paths if they were not provided.
        """

        if self.word_bank_csv is None:
            self.word_bank_csv = self.data_folder / "word-bank.csv"

        if self.valid_words_csv is None:
            self.valid_words_csv = self.data_folder / "valid-words.csv"

        return self
