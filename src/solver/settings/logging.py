from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class LogLevel(StrEnum):
    """
    Enumeration of standard logging levels.

    Attributes:
        DEBUG (str): Debug level logging.
        INFO (str): Info level logging.
        WARNING (str): Warning level logging.
        ERROR (str): Error level logging.
        CRITICAL (str): Critical level logging.
    """

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LoggingSettings(BaseModel):
    """
    Settings related to logging configuration.

    Attributes:
        level (LogLevel): The logging level for the application.
        format (str): The format for log messages as a string.
    """

    model_config = ConfigDict(
        extra="ignore"
    )

    level: LogLevel = Field(
        default=LogLevel.INFO,
        description="The logging level for the application.",
    )
    format: str = Field(
        default="console",
        description="The string identifying the logging format to use. Supported formats include 'console', 'json' and 'simple'.",
    )