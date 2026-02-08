from random import Random
from typing import List, Optional

from solver.oracle.base import Oracle


class RandomUniformOracle(Oracle):
    """
    Oracle implementation that selects a target word uniformly at random
    from the list of valid words.

    This is the assumed classic way to choose a target.
    """

    def __init__(self, rng_seed: Optional[int] = None) -> None:
        """
        Initialize the oracle with optional deterministic randomness.

        Args:
            rng_seed: Optional seed used to initialize the random number
                generator for reproducible selections.
        """
        super().__init__()
        self.random: Random = Random(rng_seed)

    def choose(self, valid_words: List[str]) -> str:
        """
        Randomly select and return one target word.

        Args:
            valid_words: List of words eligible to be selected as the target.

        Returns:
            A randomly selected word from the valid word pool.
        """
        if not valid_words:
            raise ValueError("Cannot choose a target word from an empty list.")

        return self.random.choice(valid_words)
