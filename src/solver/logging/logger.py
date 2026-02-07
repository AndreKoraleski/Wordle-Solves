from logging import Logger, StreamHandler, getLogger, WARNING
from sys import stdout

from solver.logging.format import get_formatter
from solver.settings.logging import LoggingSettings


def get_logger(settings: LoggingSettings) -> Logger:
    """
    Create and configure a logger based on the provided logging settings.

    Args:
        settings (LoggingSettings): The logging settings to configure the logger.

    Returns:
        Logger: Configured logger instance.
    """
    level = settings.level.value
    formatter = get_formatter(settings.format)

    handler = StreamHandler(stream=stdout)
    handler.setFormatter(formatter)

    root = getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)

    logger = getLogger("solver")
    logger.propagate = True

    # Noise reduction for external libraries
    # Add more libraries as needed
    libraries = []

    for library in libraries:
        library_logger = getLogger(library)
        library_logger.setLevel(WARNING)

    return logger
