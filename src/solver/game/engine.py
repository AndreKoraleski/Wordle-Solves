from logging import getLogger

from solver.game.chooser.base import Chooser
from solver.game.feedback import (
    build_feedback_decode_table,
    build_feedback_encode_table,
)
from solver.game.state import GameState
from solver.utility.load_words import load_words
from solver.strategy.base import Solver
from solver.settings.game import GameSettings
from solver.settings.path import PathSettings

logger = getLogger(__name__)


class GameEngine:
    """
    Manages the lifecycle of a Wordle game, coordinating chooser, solver,
    feedback generation, and state updates.

    Attributes:
        settings (GameSettings): Configuration related to game rules.
        paths (PathSettings): Configuration for loading word lists.
        chooser (Chooser): Component responsible for selecting the hidden answer.
        solver (Solver): Strategy responsible for generating guesses.
        feedback_encode_table: Lookup table for computing encoded feedback.
        feedback_decode_table: Lookup table for decoding feedback for display.
        state (GameState): Current mutable game state.
    """

    def __init__(
        self,
        settings: GameSettings,
        paths: PathSettings,
        chooser: Chooser,
        solver: Solver,
    ) -> None:
        """
        Initialize the game engine.

        Args:
            settings: Game configuration settings.
            paths: Word list path settings.
            chooser: Answer selection strategy.
            solver: Guess generation strategy.
        """
        self.settings = settings
        self.paths = paths
        self.chooser = chooser
        self.solver = solver

        self.feedback_encode_table = build_feedback_encode_table()
        self.feedback_decode_table = build_feedback_decode_table()

        # Initialize state
        self.state = GameState()
        self.state.valid_words = load_words(self.paths.valid_words_csv)
        self.state.word_bank = load_words(self.paths.word_bank_csv)
        self.state.max_turns = self.settings.max_turns

        logger.info("Game engine initialized.")

    def play_turn(self) -> tuple[str, int]:
        """
        Execute a single solver turn.

        Returns:
            tuple[str, int]: The guess and encoded feedback.
        """
        if self.state.terminal:
            logger.error("Cannot play turn: game has already terminated.")
            raise RuntimeError("Cannot play turn: game has already terminated.")

        if self.state.answer is None:
            raise RuntimeError("Cannot play turn: hidden answer has not been set.")

        guess = self.solver.guess(self.state)

        feedback = self.feedback_encode_table[guess][self.state.answer]

        self.state.history.append((guess, feedback))

        logger.info(
            f"Turn {len(self.state.history)}: Guess='{guess}', "
            f"Feedback='{self.feedback_decode_table[feedback]}'"
        )

        return guess, feedback

    def run(self) -> GameState:
        """
        Execute the game until termination.

        This method triggers a reset before starting to ensure a clean state
        and a fresh hidden answer.

        Returns:
            GameState: Final state after game completion.
        """
        self.reset()
        logger.info("Starting game execution.")

        while not self.state.terminal:
            self.play_turn()

        if self.state.won:
            logger.info(f"Game won in {len(self.state.history)} turns.")
        else:
            logger.info(f"Game lost. The answer was '{self.state.answer}'.")

        return self.state

    def reset(self) -> None:
        """
        Reset the game state to start a new game.

        Keep the loaded word lists and settings, but select a new hidden answer,
        clear the guess history, and reset the solver if applicable.
        """
        logger.debug("Resetting game state and solver.")
        self.state.history.clear()
        self.state.answer = self.chooser.choose()
        logger.debug(f"New answer chosen: {self.state.answer}")

        if hasattr(self.solver, "reset") and callable(self.solver.reset):
            self.solver.reset()
            logger.debug("Solver reset called.")
