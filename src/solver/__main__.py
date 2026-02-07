from solver.game.engine import GameEngine
from solver.game.chooser.impl.random_uniform import RandomUniformChooser
from solver.logging.logger import get_logger
from solver.settings.root import Settings
from solver.strategy.impl.random_uniform import RandomUniformSolver


def main() -> None:
    settings = Settings()
    logger = get_logger(settings.logging)

    chooser = RandomUniformChooser(rng_seed=42)
    solver = RandomUniformSolver(rng_seed=42)

    engine = GameEngine(
        settings=settings.game,
        paths=settings.path,
        chooser=chooser,
        solver=solver,
    )
    final_state = engine.run()
    logger.info(
        f"Game finished. Final state: {final_state.won}, Turns taken: {len(final_state.history)}"
    )


if __name__ == "__main__":
    main()
