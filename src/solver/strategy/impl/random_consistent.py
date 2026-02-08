from random import Random
from typing import List, Optional

from solver.game.state import GameState
from solver.strategy.base import Solver


class RandomConsistentSolver(Solver):
    """
    Random Consistent Guess solver.

    This solver maintains a candidate set of all words that are consistent
    with the feedback received so far and selects uniformly at random from
    this set.
    """

    def __init__(self, rng_seed: Optional[int] = None) -> None:
        """
        Initialize the solver with optional deterministic randomness.

        Args:
            rng_seed (Optional[int]): Optional seed used to initialize the random number
                generator for reproducible guess selection.
        """
        super().__init__()
        self.random: Random = Random(rng_seed)
        self.candidates: Optional[List[str]] = None
        self._processed_turns: int = 0

    def guess(self, state: GameState) -> str:
        """
        Produce a guess based on the current game state.

        Args:
            state (GameState): Current game state.

        Returns:
            str: A guessed word.
        """
        self._update_candidates(state)

        if self.candidates is None:
            self.candidates = state.valid_words.copy()

        return self.random.choice(self.candidates)

    def _update_candidates(self, state: GameState) -> None:
        """
        Update candidate list using the latest feedback in state history.

        This method only processes new history entries that have not yet
        been incorporated into the candidate list.

        Args:
            state (GameState): Current game state containing history and word pools.
        """
        # Nothing new to process
        if len(state.history) == self._processed_turns:
            return

        # Initialize candidates if necessary
        if self.candidates is None:
            self.candidates = state.valid_words.copy()

        last_guess, last_feedback = state.history[-1]

        guess_index = state.word_bank_index[last_guess]

        self.candidates = [
            word
            for word in self.candidates
            if state.feedback_encode_table[guess_index][state.valid_word_index[word]]
            == last_feedback
        ]

        self._processed_turns += 1

    def reset(self) -> None:
        """
        Reset solver internal state for a new game.
        """
        self.candidates = None
        self._processed_turns = 0
