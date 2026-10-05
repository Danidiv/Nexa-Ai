"""Setup 4.29: safe gateway runtime recovery orchestration."""
from __future__ import annotations
from pathlib import Path
from typing import Any


class GatewayRuntimeRecovery:
    """Coordinate snapshot and event-log restoration without exposing secrets."""

    VERSION = 1

    def __init__(self, gateway):
        self.gateway = gateway

    def restore(self, snapshot_path: str | None = None, event_log_path: str | None = None) -> dict[str, Any]:
        """Restore available runtime state and return a safe recovery report.

        Each source is handled independently. A bad snapshot does not erase an
        existing in-memory state, and a bad event log does not prevent a valid
        snapshot from being restored.
        """
        snapshot_target = Path(snapshot_path or self.gateway.snapshot_path).absolute()
        event_target = Path(event_log_path or self.gateway.event_log_path).absolute()
        report: dict[str, Any] = {
            "recovery_version": self.VERSION,
            "snapshot": {"path": str(snapshot_target), "status": "missing", "restored": False},
            "event_log": {"path": str(event_target), "status": "missing", "restored": False, "entries": 0},
        }

        if snapshot_target.exists():
            try:
                self.gateway.load_snapshot(str(snapshot_target))
                report["snapshot"]["status"] = "restored"
                report["snapshot"]["restored"] = True
            except (OSError, ValueError, TypeError) as exc:
                report["snapshot"]["status"] = "rejected"
                report["snapshot"]["error"] = f"{type(exc).__name__}: {exc}"

        if event_target.exists():
            try:
                count = self.gateway.load_event_log(str(event_target))
                report["event_log"]["status"] = "restored"
                report["event_log"]["restored"] = True
                report["event_log"]["entries"] = int(count)
            except (OSError, ValueError, TypeError) as exc:
                report["event_log"]["status"] = "rejected"
                report["event_log"]["error"] = f"{type(exc).__name__}: {exc}"

        report["restored_any"] = bool(report["snapshot"]["restored"] or report["event_log"]["restored"])
        report["safe"] = True
        return report

