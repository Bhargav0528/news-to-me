"""Lightweight atomic status file tracker for pipeline runs.

Writes run progress to data/pipeline_status.json atomically (write-to-temp + rename)
so that a partial write is never read by a concurrent process or crash observer.

Usage:
    from pipeline.status import status
    status.start(stage="generate", steps=["ingest", "tldr", "news_bangalore", ...])
    status.set_step("tldr")           # marks tldr complete, current = tldr
    status.set_step("news_bangalore") # marks news_bangalore complete
    status.complete()                 # stage = "completed"
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATUS_FILE = Path("data/pipeline_status.json")

# Canonical step ordering for the generate stage.
# Each call to set_step() marks the previous step as completed and
# updates current_step to the newly started one.
GENERATE_STEPS = [
    "tldr",
    "news_bangalore",
    "news_karnataka",
    "news_india",
    "news_us",
    "news_world",
    "biztech",
    "growth",
    "knowledge",
    "fun",
]


def _write_atomically(data: dict[str, Any], path: Path) -> None:
    """Write data to path atomically: write to .tmp, then rename."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2))
    os.replace(tmp, path)


def start(
    stage: str,
    steps: list[str] | None = None,
    run_id: str | None = None,
) -> None:
    """Initialize a new run record.

    Args:
        stage: "ingest" or "generate".
        steps: Ordered list of step names. Required for stage="generate";
               for stage="ingest" this is ignored.
        run_id: ISO timestamp string. Defaults to now UTC.
    """
    if run_id is None:
        run_id = datetime.now(timezone.utc).isoformat()

    data: dict[str, Any] = {
        "run_id": run_id,
        "stage": stage,
        "current_step": "",
        "steps_completed": [],
        "steps_remaining": list(steps) if steps else [],
        "started_at": run_id,
        "updated_at": run_id,
    }
    _write_atomically(data, STATUS_FILE)


def set_step(step_name: str) -> None:
    """Mark the current step as completed and advance to step_name.

    On the first call (no current_step yet), current_step is set to step_name
    and step_name is NOT added to steps_completed (it's still in progress).
    On subsequent calls, the previous current_step moves to steps_completed
    before advancing.

    Invariant after this call: current_step is NEVER in steps_remaining.
    """
    if not STATUS_FILE.exists():
        return  # No active run — nothing to update.

    prev = _read() or {}
    completed = list(prev.get("steps_completed", []))
    remaining = list(prev.get("steps_remaining", []))

    current = prev.get("current_step", "")
    if current and current not in completed:
        # Advance: previous step is now done.
        completed.append(current)
        remaining = [r for r in remaining if r != current]

    # step_name is now the current step — it must NOT be in remaining.
    remaining = [r for r in remaining if r != step_name]

    now = datetime.now(timezone.utc).isoformat()
    _write_atomically(
        {
            **prev,
            "current_step": step_name,
            "steps_completed": completed,
            "steps_remaining": remaining,
            "updated_at": now,
        },
        STATUS_FILE,
    )


def complete() -> None:
    """Mark the current run as successfully completed."""
    if not STATUS_FILE.exists():
        return
    prev = _read() or {}
    now = datetime.now(timezone.utc).isoformat()

    # Move whatever was in progress to completed.
    current = prev.get("current_step", "")
    completed = list(prev.get("steps_completed", []))
    remaining = list(prev.get("steps_remaining", []))
    if current and current not in completed:
        completed.append(current)
        remaining = [r for r in remaining if r != current]

    _write_atomically(
        {
            **prev,
            "stage": "completed",
            "current_step": "",
            "steps_completed": completed,
            "steps_remaining": remaining,
            "updated_at": now,
        },
        STATUS_FILE,
    )


def fail(failure_message: str | None = None) -> None:
    """Mark the current run as failed, recording the failure message."""
    if not STATUS_FILE.exists():
        return
    prev = _read() or {}
    now = datetime.now(timezone.utc).isoformat()

    _write_atomically(
        {
            **prev,
            "stage": "failed",
            "current_step": prev.get("current_step", ""),
            "updated_at": now,
            **({"failure_message": failure_message} if failure_message else {}),
        },
        STATUS_FILE,
    )


def get_status() -> dict[str, Any] | None:
    """Return the current status record, or None if no run is in progress."""
    return _read()


def _read() -> dict[str, Any] | None:
    """Read and return the current status record."""
    if not STATUS_FILE.exists():
        return None
    try:
        return json.loads(STATUS_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return None
