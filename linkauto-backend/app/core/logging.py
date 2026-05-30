import contextvars
import logging
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# ContextVar to store the correlation/trace ID async-safely
correlation_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar(
    "correlation_id", default=""
)


class CorrelationIDFilter(logging.Filter):
    """Logging filter to inject the current correlation ID into log records."""
    def filter(self, record):
        record.correlation_id = correlation_id_ctx.get() or "no-trace"
        return True


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """FastAPI Middleware to manage the correlation ID context for each request."""
    async def dispatch(self, request: Request, call_next):
        # Extract from header or generate a new unique UUID4
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        
        # Set the context variable
        token = correlation_id_ctx.set(correlation_id)
        try:
            response = await call_next(request)
            # Add to response header for debugging/traceability
            response.headers["X-Correlation-ID"] = correlation_id
            return response
        finally:
            # Clean up/reset context var
            correlation_id_ctx.reset(token)


def setup_logging():
    """Configures the logging system with the trace/correlation ID filter and standard format."""
    # Create the filter
    corr_filter = CorrelationIDFilter()

    # Formatter including timestamp, level, correlation_id, logger name, and message
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [Trace:%(correlation_id)s] %(name)s: %(message)s"
    )

    # Standard stream handler
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.addFilter(corr_filter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers
    root_logger.handlers = [handler]

    # Apply filter to uvicorn loggers as well
    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        log = logging.getLogger(logger_name)
        log.handlers = []
        log.addHandler(handler)
        log.propagate = False
