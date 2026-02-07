from abc import ABC, abstractmethod

from solver.game.state import GameState


class Solver(ABC):
    """
    Base interface for any Wordle solving strategy.

    A strategy receives the current GameState and must return
    a valid 5-letter guess word.
    """

    @abstractmethod
    def solve(self, state: GameState) -> str:
        """
        Produce the next guess based on the current game state.

        Args:
            state (GameState): Current game state snapshot.

        Returns:
            str: A valid 5-letter lowercase guess.
        """
        ...
