from random import Random
from typing import List, Optional

from solver.game.chooser.base import Chooser


class RandomUniformChooser(Chooser):
    """
    Chooser implementation that selects a target word uniformly at random
    from the list of valid words.

    This is the assumed classic way to choose a target.
    """

    def __init__(self, valid_words: List[str], rng_seed: Optional[int] = None) -> None:
        """
        Initialize the chooser with optional deterministic randomness.

        Args:
            valid_words: List of words eligible to be selected.
            rng_seed: Optional seed used to initialize the random number
                generator for reproducible selections.
        """
        super().__init__(valid_words)
        self.random: Random = Random(rng_seed)

    def choose(self) -> str:
        """
        Randomly select and return one target word.

        Returns:
            A randomly selected word from the valid word pool.
        """
        return self.random.choice(self.valid_words)
