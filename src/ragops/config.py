from __future__ import annotations

import tomllib
from pathlib import Path

from ragops.models import RegressionPolicy


def load_regression_policy(path: str | Path) -> RegressionPolicy:
    try:
        data = tomllib.loads(Path(path).read_text(encoding="utf-8"))
        return RegressionPolicy(**data["regression"])
    except (OSError, tomllib.TOMLDecodeError, KeyError, TypeError) as exc:
        raise ValueError(f"Invalid regression policy {path}: {exc}") from exc
