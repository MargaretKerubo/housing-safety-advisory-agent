import logging
import time
from functools import wraps
from typing import Callable, Type, Tuple

logger = logging.getLogger(__name__)


class RetryableError(Exception):
    """Error that should be retried (network issues, rate limits, timeouts)."""


class NonRetryableError(Exception):
    """Error that should NOT be retried (bad input, auth failures)."""


# Common exception types that warrant a retry
_RETRYABLE_EXCEPTIONS: Tuple[Type[Exception], ...] = (
    ConnectionError,
    TimeoutError,
)


def retry_call(
    fn: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    backoff: float = 2.0,
    retryable_exceptions: Tuple[Type[Exception], ...] = None,
    **kwargs,
) -> str:
    """
    Call `fn(**kwargs)` with retry logic and exponential backoff.

    Args:
        fn: The callable to invoke.
        max_retries: Maximum number of retry attempts (default 3).
        base_delay: Seconds to wait before first retry (default 1.0).
        backoff: Multiplier for delay after each retry (default 2.0).
        retryable_exceptions: Tuple of exception types that trigger a retry.
        **kwargs: Passed through to `fn`.

    Returns:
        The return value of `fn(**kwargs)`.

    Raises:
        The last exception encountered if all retries are exhausted.
    """
    if retryable_exceptions is None:
        retryable_exceptions = _RETRYABLE_EXCEPTIONS

    last_exception = None

    for attempt in range(1, max_retries + 1):
        try:
            return fn(**kwargs)
        except retryable_exceptions as e:
            last_exception = e
            if attempt < max_retries:
                delay = base_delay * (backoff ** (attempt - 1))
                logger.warning(
                    "Retryable error (attempt %d/%d): %s. Retrying in %.1fs...",
                    attempt, max_retries, e, delay,
                )
                time.sleep(delay)
            else:
                logger.error(
                    "All %d retries exhausted for %s. Last error: %s",
                    max_retries, fn.__name__, e,
                )
        except NonRetryableError:
            raise
        except Exception as e:
            # Non-retryable exceptions bubble up immediately
            logger.error("Non-retryable error in %s: %s", fn.__name__, e)
            raise

    raise last_exception


def retryable(max_retries: int = 3, base_delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator that applies retry logic to a function.

    Usage:
        @retryable(max_retries=3)
        def my_func():
            ...
    """
    def decorator(fn: Callable):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            return retry_call(
                fn,
                max_retries=max_retries,
                base_delay=base_delay,
                backoff=backoff,
                *args,
                **kwargs,
            )
        return wrapper
    return decorator
