"""Turn wrongly typed input into the loader's own contract error instead of a crash."""

from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])
WRONG_TYPE = (TypeError, AttributeError, KeyError, OverflowError)


def contract_guard(error: type[Exception], what: str) -> Callable[[F], F]:
    """Re-raise TypeError/AttributeError/KeyError from a loader as ``error``."""

    def decorate(function: F) -> F:
        @functools.wraps(function)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return function(*args, **kwargs)
            except WRONG_TYPE as exc:
                raise error(f"Invalid {what}: wrong value type or missing field ({exc})") from exc

        return wrapper  # type: ignore[return-value]

    return decorate
