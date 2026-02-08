from random import Random
from typing import Optional

from solver.game.state import GameState
from solver.strategy.base import Solver


class RandomUniformSolver(Solver):
    """
    Solver implementation that selects a guess uniformly at random.

    The solver can optionally choose from either:
        - The full word bank (all allowed guesses), or
        - The valid answer pool only.
    """

    def __init__(
        self, rng_seed: Optional[int] = None, choose_from_answers: bool = False
    ) -> None:
        """
        Initialize the solver with optional deterministic randomness.

        Args:
            rng_seed: Optional seed used to initialize the random number
                generator for reproducible guess selection.
            choose_from_answers: If True, guesses are sampled from the valid
                answer list only. Otherwise, guesses are sampled from the
                entire word bank (all allowed guesses).
        """
        super().__init__()
        self.random: Random = Random(rng_seed)
        self.choose_from_answers: bool = choose_from_answers

    def guess(self, state: GameState) -> str:
        """
        Select and return a random guess word.

        Args:
            state: Current game state containing word pools.

        Returns:
            str: A randomly selected guess word.
        """
        if self.choose_from_answers:
            return self.random.choice(state.valid_words)

        return self.random.choice(state.word_bank)

    def reset(self) -> None:
        """
        Reset any internal solver state for a new game.
        """
        pass
