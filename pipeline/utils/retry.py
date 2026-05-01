"""Retry helpers with exponential backoff for the News To Me pipeline.

Usage:
    from pipeline.utils.retry import llm_retry, http_retry

    @llm_retry
    def my_llm_call(prompt, user):
        ...

    @http_retry
    def fetch_url(url):
        ...
"""

from __future__ import annotations

import functools
import logging
import time
from typing import Any, Callable, TypeVar

LOGGER = logging.getLogger(__name__)

T = TypeVar("T")


def _retry(
    func: Callable[..., T],
    max_attempts: int,
    base_delay: float,
    exponential: bool,
    retry_on: tuple[type[Exception], ...],
    logger: logging.Logger,
    operation_name: str,
) -> T:
    """Generic retry wrapper with exponential backoff."""
    last_exc: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return func()
        except retry_on as exc:
            last_exc = exc
            if attempt == max_attempts:
                logger.error(
                    "%s failed after %d attempts: %s",
                    operation_name,
                    max_attempts,
                    exc,
                )
                raise
            delay = base_delay * (2 ** (attempt - 1)) if exponential else base_delay
            logger.warning(
                "%s attempt %d/%d failed: %s. Retrying in %.1fs...",
                operation_name,
                attempt,
                max_attempts,
                exc,
                delay,
            )
            time.sleep(delay)
    # Should never reach here, but satisfies type checker
    raise last_exc  # type: ignore[possibly-undefined]


def llm_retry(func: Callable[..., T]) -> T:
    """Retry decorator for LLM API calls. 2 attempts, exponential backoff starting at 1s.

    Retries on: Exception (all LLM errors).
    Logs at WARN on retry, ERROR on final failure.
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        return _retry(
            lambda: func(*args, **kwargs),
            max_attempts=2,
            base_delay=1.0,
            exponential=True,
            retry_on=(Exception,),
            logger=LOGGER,
            operation_name=f"LLM call ({func.__name__})",
        )
    return wrapper


def http_retry(func: Callable[..., T]) -> T:
    """Retry decorator for HTTP calls. 2 attempts, linear backoff at 5s.

    Retries on: Exception (all HTTP errors).
    Logs at WARN on retry, ERROR on final failure.
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        return _retry(
            lambda: func(*args, **kwargs),
            max_attempts=2,
            base_delay=5.0,
            exponential=False,
            retry_on=(Exception,),
            logger=LOGGER,
            operation_name=f"HTTP call ({func.__name__})",
        )
    return wrapper


def git_retry(func: Callable[..., T]) -> T:
    """Retry decorator for git operations. 2 attempts, linear backoff at 10s.

    Retries on: Exception (network issues, transient git errors).
    Logs at WARN on retry, ERROR on final failure.
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        return _retry(
            lambda: func(*args, **kwargs),
            max_attempts=2,
            base_delay=10.0,
            exponential=False,
            retry_on=(Exception,),
            logger=LOGGER,
            operation_name=f"Git operation ({func.__name__})",
        )
    return wrapper