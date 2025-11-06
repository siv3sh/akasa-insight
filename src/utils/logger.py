"""
Logger module for centralized logging configuration with JSON support.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for logging."""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


class Logger:
    """
    Centralized logger for the application with JSON support.
    """

    _loggers = {}

    @classmethod
    def get_logger(cls, name: str, log_file: Optional[str] = None) -> logging.Logger:
        """
        Get or create a logger instance with JSON formatting.

        Args:
            name: Name of the logger (usually __name__)
            log_file: Optional path to log file

        Returns:
            logging.Logger: Configured logger instance
        """
        if name in cls._loggers:
            return cls._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        # Avoid adding handlers multiple times
        if not logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

            # File handler with JSON formatting
            if log_file:
                log_path = Path(log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)

                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(logging.DEBUG)
                file_formatter = JSONFormatter()
                file_handler.setFormatter(file_formatter)
                logger.addHandler(file_handler)

        cls._loggers[name] = logger
        return logger

    @classmethod
    def get_json_logger(cls, name: str, log_file: str) -> logging.Logger:
        """
        Get a logger that outputs only JSON to file.

        Args:
            name: Name of the logger
            log_file: Path to log file

        Returns:
            logging.Logger: JSON-only logger instance
        """
        logger = logging.getLogger(f"{name}_json")
        logger.setLevel(logging.DEBUG)

        # Clear any existing handlers
        logger.handlers.clear()

        # File handler with JSON formatting only
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = JSONFormatter()
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        return logger

    @classmethod
    def log_error(cls, logger: logging.Logger, error: Exception, context: str = ""):
        """
        Log error with context information.

        Args:
            logger: Logger instance
            error: Exception object
            context: Additional context about where the error occurred
        """
        error_msg = (
            f"{context}: {type(error).__name__} - {str(error)}"
            if context
            else str(error)
        )
        logger.error(error_msg, exc_info=True)

    @classmethod
    def log_data_quality_issue(
        cls, logger: logging.Logger, issue_type: str, details: dict
    ):
        """
        Log data quality issues in a structured format.

        Args:
            logger: Logger instance
            issue_type: Type of data quality issue
            details: Dictionary with issue details
        """
        log_message = f"DATA QUALITY ISSUE - {issue_type}: {details}"
        logger.warning(log_message)

    @classmethod
    def log_ingestion_lineage(
        cls,
        logger: logging.Logger,
        file_name: str,
        load_time: str,
        record_count: int,
        validation_status: str,
        checksum: str,
    ):
        """
        Log ingestion lineage information.

        Args:
            logger: Logger instance
            file_name: Name of the file processed
            load_time: Time when the file was loaded
            record_count: Number of records processed
            validation_status: Status of data validation
            checksum: Checksum of the file
        """
        log_message = (
            f"INGESTION LINEAGE - File: {file_name}, "
            f"Load Time: {load_time}, "
            f"Records: {record_count}, "
            f"Validation: {validation_status}, "
            f"Checksum: {checksum}"
        )
        logger.info(log_message)
