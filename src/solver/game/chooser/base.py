from abc import ABC, abstractmethod
from typing import List


class Chooser(ABC):
    """
    Abstract base class responsible for selecting a target word
    for a Wordle game or simulation.

    The objective is to allow custom implementations to provide
    different word selection policies or distributions for solver
    evaluation and experimentation.
    """

    def __init__(self, valid_words: List[str]) -> None:
        """
        Initialize the chooser with a list of possible target words.

        Args:
            valid_words: A list containing all valid words that can be
                selected as the hidden target word.

        Raises:
            ValueError: If the provided list of target words is empty.
        """
        if not valid_words:
            raise ValueError("valid_words cannot be empty")

        self.valid_words: List[str] = valid_words

    @abstractmethod
    def choose(self) -> str:
        """
        Select and return one target word from the available pool.

        Returns:
            A string representing the selected target word.
        """
        ...
