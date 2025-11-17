"""
Structured Error Logging Utility
Provides centralized error logging with correlation IDs and context
"""

import logging
import traceback
import json
import uuid
from typing import Optional, Dict, Any
from datetime import datetime
from contextvars import ContextVar

# Context variable for correlation ID (thread-safe)
correlation_id_var: ContextVar[str] = ContextVar('correlation_id', default='')

class StructuredLogger:
    """
    Structured logger with correlation ID tracking and context capture
    """

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.name = name

    @staticmethod
    def generate_correlation_id() -> str:
        """Generate a unique correlation ID"""
        return str(uuid.uuid4())

    @staticmethod
    def set_correlation_id(correlation_id: str) -> None:
        """Set the current correlation ID"""
        correlation_id_var.set(correlation_id)

    @staticmethod
    def get_correlation_id() -> str:
        """Get the current correlation ID"""
        return correlation_id_var.get()

    def _build_log_context(
        self,
        message: str,
        error_type: Optional[str] = None,
        error_code: Optional[int] = None,
        status_code: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
        stack_trace: Optional[str] = None
    ) -> Dict[str, Any]:
        """Build structured log context"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'logger': self.name,
            'message': message,
            'correlation_id': self.get_correlation_id(),
        }

        if error_type:
            log_entry['error_type'] = error_type
        if error_code:
            log_entry['error_code'] = error_code
        if status_code:
            log_entry['status_code'] = status_code
        if context:
            log_entry['context'] = context
        if stack_trace:
            log_entry['stack_trace'] = stack_trace

        return log_entry

    def info(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log info message with context"""
        log_context = self._build_log_context(message, context=context)
        self.logger.info(json.dumps(log_context))

    def warning(self, message: str, error_type: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> None:
        """Log warning message with context"""
        log_context = self._build_log_context(message, error_type=error_type, context=context)
        self.logger.warning(json.dumps(log_context))

    def error(
        self,
        message: str,
        error_type: Optional[str] = None,
        status_code: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
        exc_info: bool = False
    ) -> None:
        """Log error message with context and optional stack trace"""
        stack_trace = None
        if exc_info:
            stack_trace = traceback.format_exc()

        log_context = self._build_log_context(
            message,
            error_type=error_type,
            status_code=status_code,
            context=context,
            stack_trace=stack_trace
        )
        self.logger.error(json.dumps(log_context))

    def critical(
        self,
        message: str,
        error_type: Optional[str] = None,
        status_code: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
        exc_info: bool = False
    ) -> None:
        """Log critical error with context and optional stack trace"""
        stack_trace = None
        if exc_info:
            stack_trace = traceback.format_exc()

        log_context = self._build_log_context(
            message,
            error_type=error_type,
            status_code=status_code,
            context=context,
            stack_trace=stack_trace
        )
        self.logger.critical(json.dumps(log_context))

    def exception(
        self,
        message: str,
        error_type: Optional[str] = None,
        status_code: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log exception with full context"""
        stack_trace = traceback.format_exc()
        log_context = self._build_log_context(
            message,
            error_type=error_type,
            status_code=status_code,
            context=context,
            stack_trace=stack_trace
        )
        self.logger.error(json.dumps(log_context))


def configure_logging(log_level: str = 'INFO') -> None:
    """
    Configure structured logging for the application

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(message)s',  # We're using JSON structured logging
        datefmt='%Y-%m-%dT%H:%M:%SZ'
    )


# Convenience function to get logger
def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance"""
    return StructuredLogger(name)
