from datetime import datetime, timezone
from json import dumps
from logging import Formatter, LogRecord as Record


def _format_timestamp(time: float) -> str:
    """
    Format the timestamp of the log record to a UTC datetime object.

    Args:
        record (Record): The log record.
    Returns:
        str: The UTC datetime representation of the log record's timestamp in ISO 8601 format.
    """
    return datetime.fromtimestamp(time, tz=timezone.utc).isoformat()


def get_formatter(format_type: str) -> Formatter:
    """
    Get the appropriate formatter based on the format type.

    Args:
        format_type (str): The type of format ('console', 'json', 'simple').
    Returns:
        Formatter: The corresponding formatter instance.
    """
    formatters = {
        "console": ConsoleFormatter(),
        "json": JsonFormatter(),
        "simple": SimpleFormatter(),
    }
    return formatters.get(format_type.lower(), ConsoleFormatter())


class ConsoleFormatter(Formatter):
    """
    A logging formatter that outputs log records in a human-readable console format.
    """

    def format(self, record: Record) -> str:
        """
        Format the log record for console output.

        Args:
            record (Record): The log record.
        Returns:
            str: The formatted log record string.
        """
        timestamp = _format_timestamp(record.created)
        return (
            f"[{timestamp}] {record.levelname} - {record.name} - {record.getMessage()}"
        )


class JsonFormatter(Formatter):
    """
    A logging formatter that outputs log records in JSON format.
    """

    def format(self, record: Record) -> str:
        """
        Format the log record as a JSON string.

        Args:
            record (Record): The log record.
        Returns:
            str: The JSON representation of the log record.
        """

        log_record = {
            "timestamp": _format_timestamp(record.created),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "file": record.filename,
            "line": record.lineno,
            "function": record.funcName,
        }

        return dumps(log_record)


class SimpleFormatter(Formatter):
    """
    A logging formatter that outputs log records in a simple format.
    """

    def format(self, record: Record) -> str:
        """
        Format the log record in a simple format.

        Args:
            record (Record): The log record.
        Returns:
            str: The formatted log record string.
        """
        return f"{record.levelname}: {record.getMessage()}"
