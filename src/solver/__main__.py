from solver.logging.logger import get_logger
from solver.oracle.impl.random_uniform import RandomUniformOracle
from solver.settings.root import Settings
from solver.statistics.benchmark import run_benchmark
from solver.statistics.export import save_benchmark_results
from solver.strategy.impl.random_consistent import RandomConsistentSolver
from solver.strategy.impl.random_uniform import RandomUniformSolver


def main() -> None:
    settings = Settings()
    logger = get_logger(settings.logging)

    logger.info("=" * 80)
    logger.info("Starting Wordle Solver Benchmark")
    logger.info("=" * 80)

    # Create oracle instance (shared across strategies)
    oracle = RandomUniformOracle()

    batches = []

    # Benchmark 1: Random Consistent
    logger.info("Strategy 1: Random Consistent")
    solver_consistent = RandomConsistentSolver()
    batch_consistent = run_benchmark(
        oracle=oracle,
        solver=solver_consistent,
        oracle_name="Random Uniform Oracle",
        strategy_name="Random Consistent",
        game_settings=settings.game,
        path_settings=settings.path,
        settings_snapshot=settings.model_dump(),
    )
    batches.append(batch_consistent)

    # Benchmark 2: Random Uniform
    logger.info("")
    logger.info("Strategy 2: Random Uniform")
    solver_uniform = RandomUniformSolver()
    batch_uniform = run_benchmark(
        oracle=oracle,
        solver=solver_uniform,
        oracle_name="Random Uniform Oracle",
        strategy_name="Random Uniform",
        game_settings=settings.game,
        path_settings=settings.path,
        settings_snapshot=settings.model_dump(),
    )
    batches.append(batch_uniform)

    # Save results
    logger.info("")
    logger.info("=" * 80)
    logger.info("Saving results...")
    logger.info("=" * 80)
    save_benchmark_results(batches, settings.path)

    logger.info("=" * 80)
    logger.info("Benchmark complete!")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
