"""
Request/Response Logging Middleware
Provides comprehensive request and response logging with performance tracking
"""

import time
import json
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from utils.error_logger import StructuredLogger, StructuredLogger as CorrLogger
import logging

logger = StructuredLogger('logging_middleware')


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging all requests and responses with correlation IDs
    """

    EXCLUDED_PATHS = {
        '/health',
        '/api/health',
        '/docs',
        '/openapi.json',
        '/favicon.ico'
    }

    async def dispatch(self, request: Request, call_next):
        """
        Process request and response with comprehensive logging
        """
        # Generate or extract correlation ID
        correlation_id = request.headers.get('X-Correlation-ID') or CorrLogger.generate_correlation_id()
        CorrLogger.set_correlation_id(correlation_id)

        # Skip logging for health checks and documentation
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)

        # Extract request info
        request_start = time.time()
        method = request.method
        path = request.url.path
        query_params = dict(request.query_params)

        # Log request start
        try:
            body = await request.body()
            body_str = body.decode('utf-8') if body else None

            # Sanitize sensitive data from body
            body_data = None
            if body_str:
                try:
                    body_data = json.loads(body_str)
                    # Remove sensitive fields
                    if isinstance(body_data, dict):
                        sensitive_fields = {'password', 'token', 'api_key', 'secret'}
                        for field in sensitive_fields:
                            if field in body_data:
                                body_data[field] = '***REDACTED***'
                except json.JSONDecodeError:
                    body_data = body_str[:200]  # Truncate if not JSON

            logger.info(
                f"Request received: {method} {path}",
                context={
                    'correlation_id': correlation_id,
                    'method': method,
                    'path': path,
                    'query_params': query_params,
                    'body': body_data,
                    'client_ip': request.client.host if request.client else 'unknown',
                    'user_agent': request.headers.get('user-agent', 'unknown')
                }
            )
        except Exception as e:
            logger.error(
                f"Failed to log request body: {str(e)}",
                error_type='LOG_ERROR',
                context={'path': path, 'method': method},
                exc_info=True
            )

        # Call the endpoint
        response = await call_next(request)

        # Calculate request duration
        request_duration = time.time() - request_start

        # Log response
        logger.info(
            f"Response sent: {method} {path} - {response.status_code}",
            context={
                'correlation_id': correlation_id,
                'method': method,
                'path': path,
                'status_code': response.status_code,
                'duration_ms': round(request_duration * 1000, 2),
                'content_length': response.headers.get('content-length', 'unknown')
            }
        )

        # Add correlation ID to response headers
        response.headers['X-Correlation-ID'] = correlation_id

        # Add timing header
        response.headers['X-Response-Time'] = str(request_duration)

        return response
