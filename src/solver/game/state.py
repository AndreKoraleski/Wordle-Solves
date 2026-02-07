from dataclasses import dataclass, field
from typing import List, Optional, Tuple


WIN_FEEDBACK: int = 242


@dataclass
class GameState:
    """
    Canonical Wordle game state.

    Attributes:
        history (List[Tuple[str, int]]): Ordered list of (guess, encoded_feedback) pairs.
        answer (Optional[str]): Hidden answer word determined by the chooser.
        word_bank (List[str]): List of all allowed guess words.
        valid_words (List[str]): List of all current valid answer words.
        max_turns (int): Maximum number of guesses allowed.
    """

    history: List[Tuple[str, int]] = field(default_factory=list)
    answer: Optional[str] = None
    word_bank: List[str] = field(default_factory=list)
    valid_words: List[str] = field(default_factory=list)
    max_turns: int = 6

    @property
    def turn(self) -> int:
        """
        Current turn index (0-based).

        Returns:
            int: Number of guesses already made.
        """
        return len(self.history)

    @property
    def remaining_turns(self) -> int:
        """
        Number of guesses remaining.

        Returns:
            int: Remaining number of guesses.
        """
        return self.max_turns - self.turn

    @property
    def terminal(self) -> bool:
        """
        Whether the game has reached a terminal state.

        Returns:
            bool:
                True if the puzzle has been solved or if the maximum
                number of turns has been reached, otherwise False.
        """
        if not self.history:
            return False

        _, last_feedback = self.history[-1]

        solved = last_feedback == WIN_FEEDBACK
        out_of_turns = self.turn >= self.max_turns

        return solved or out_of_turns

    @property
    def won(self) -> bool:
        """
        Whether the game has been won.

        Returns:
            bool: True if the last guess matched the answer, otherwise False.
        """
        if not self.history:
            return False

        _, last_feedback = self.history[-1]
        return last_feedback == WIN_FEEDBACK
