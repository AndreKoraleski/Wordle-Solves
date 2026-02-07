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

    @abstractmethod
    def choose(self, valid_words: List[str]) -> str:
        """
        Select and return one target word from the available pool.

        Args:
            valid_words: List of words eligible to be selected as the target.

        Returns:
            A string representing the selected target word.

        Raises:
            ValueError: If the valid_words list is empty.
        """
        ...
