from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from ragops.models import ComparisonReport, EvaluationReport


class ExperimentStore:
    """Small local run store; hosted backends can implement the same boundary later."""

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def save(
        self,
        report: EvaluationReport | ComparisonReport,
        *,
        label: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> str:
        run_id = uuid4().hex
        created_at = datetime.now(timezone.utc).isoformat()
        report_type = "comparison" if isinstance(report, ComparisonReport) else "evaluation"
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO runs
                    (id, created_at, scenario_id, report_type, passed, label, metadata, report)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    created_at,
                    report.scenario_id,
                    report_type,
                    int(report.passed),
                    label,
                    json.dumps(metadata or {}, ensure_ascii=False),
                    json.dumps(report.to_dict(), ensure_ascii=False),
                ),
            )
        return run_id

    def list_runs(self, *, limit: int = 20) -> list[dict[str, Any]]:
        if limit < 1 or limit > 1000:
            raise ValueError("limit must be between 1 and 1000")
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, created_at, scenario_id, report_type, passed, label, metadata
                FROM runs ORDER BY created_at DESC LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            {
                "id": row[0],
                "created_at": row[1],
                "scenario_id": row[2],
                "report_type": row[3],
                "passed": bool(row[4]),
                "label": row[5],
                "metadata": json.loads(row[6]),
            }
            for row in rows
        ]

    def get_report(self, run_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute("SELECT report FROM runs WHERE id = ?", (run_id,)).fetchone()
        return json.loads(row[0]) if row else None

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    scenario_id TEXT NOT NULL,
                    report_type TEXT NOT NULL,
                    passed INTEGER NOT NULL,
                    label TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    report TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_runs_scenario_created "
                "ON runs(scenario_id, created_at DESC)"
            )
