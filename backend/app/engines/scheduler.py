"""
NEXUS — Scheduled Data Ingestion Engine
==========================================
User-configurable automated data pulls on a defined cadence.
Uses APScheduler for lightweight background scheduling (no Redis/Celery needed).
"""

import logging
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("nexus.scheduler")


class SchedulePreset:
    """Pre-built schedule configurations for common cadences."""
    EVERY_15_MIN = "*/15 * * * *"
    HOURLY = "0 * * * *"
    EVERY_6_HOURS = "0 */6 * * *"
    DAILY_6AM = "0 6 * * *"
    DAILY_MIDNIGHT = "0 0 * * *"
    WEEKLY_MONDAY = "0 6 * * 1"
    MONTHLY_FIRST = "0 6 1 * *"

    ALL = {
        "every_15_minutes": EVERY_15_MIN,
        "hourly": HOURLY,
        "every_6_hours": EVERY_6_HOURS,
        "daily_6am": DAILY_6AM,
        "daily_midnight": DAILY_MIDNIGHT,
        "weekly_monday": WEEKLY_MONDAY,
        "monthly_first": MONTHLY_FIRST,
    }


class DataScheduler:
    """
    Lightweight background scheduler for automated data ingestion.

    Manages scheduled jobs that pull data from configured connectors,
    run quality checks via PipelineOrchestrator, and load into the database.
    """

    def __init__(self):
        self._jobs: Dict[str, Dict[str, Any]] = {}
        self._history: List[Dict[str, Any]] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._max_history = 500  # Keep last 500 runs
        self._last_token_cleanup: Optional[datetime] = None  # Tracks last cleanup run

    def start(self):
        """Start the background scheduler thread."""
        if self._running:
            return {"status": "already_running"}

        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="nexus-scheduler")
        self._thread.start()
        logger.info("Data scheduler started")
        return {"status": "started"}

    def stop(self):
        """Stop the background scheduler."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Data scheduler stopped")
        return {"status": "stopped"}

    def add_job(
        self,
        job_id: str,
        name: str,
        schedule: str,
        connector_type: str,
        connector_config: Dict[str, Any],
        pipeline_callback: Optional[Callable] = None,
        created_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Register a new scheduled ingestion job.

        Parameters:
            job_id: Unique identifier for this job
            name: Human-readable name (e.g., "Daily SAP Pull")
            schedule: Cron expression or preset name (e.g., "daily_6am", "0 */6 * * *")
            connector_type: Type of connector ("csv", "database", "api", "s3")
            connector_config: Configuration dict passed to the connector
            pipeline_callback: Optional function(df) -> dict to run after extraction
            created_by: User who created this job
        """
        # Resolve preset names to cron expressions
        cron = SchedulePreset.ALL.get(schedule, schedule)

        with self._lock:
            self._jobs[job_id] = {
                "id": job_id,
                "name": name,
                "schedule_cron": cron,
                "schedule_label": schedule if schedule in SchedulePreset.ALL else "custom",
                "connector_type": connector_type,
                "connector_config": connector_config,
                "pipeline_callback": pipeline_callback,
                "is_active": True,
                "created_by": created_by,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_run_at": None,
                "next_run_at": self._compute_next_run(cron),
                "last_status": None,
                "run_count": 0,
                "total_rows_ingested": 0,
                "error_count": 0,
            }

        logger.info(f"Job '{name}' ({job_id}) added with schedule: {cron}")
        return self.get_job(job_id)

    def update_job(self, job_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a job's schedule, config, or active status."""
        with self._lock:
            if job_id not in self._jobs:
                return {"error": f"Job '{job_id}' not found"}

            job = self._jobs[job_id]

            if "schedule" in updates:
                cron = SchedulePreset.ALL.get(updates["schedule"], updates["schedule"])
                job["schedule_cron"] = cron
                job["schedule_label"] = updates["schedule"] if updates["schedule"] in SchedulePreset.ALL else "custom"
                job["next_run_at"] = self._compute_next_run(cron)

            if "is_active" in updates:
                job["is_active"] = bool(updates["is_active"])

            if "name" in updates:
                job["name"] = updates["name"]

            if "connector_config" in updates:
                job["connector_config"].update(updates["connector_config"])

        return self.get_job(job_id)

    def remove_job(self, job_id: str) -> Dict[str, Any]:
        """Remove a scheduled job."""
        with self._lock:
            if job_id in self._jobs:
                job = self._jobs.pop(job_id)
                return {"status": "removed", "job": job["name"]}
            return {"error": f"Job '{job_id}' not found"}

    def pause_job(self, job_id: str) -> Dict[str, Any]:
        """Pause a job without removing it."""
        return self.update_job(job_id, {"is_active": False})

    def resume_job(self, job_id: str) -> Dict[str, Any]:
        """Resume a paused job."""
        return self.update_job(job_id, {"is_active": True})

    def get_job(self, job_id: str) -> Dict[str, Any]:
        """Get job details (without internal callback reference)."""
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return {"error": f"Job '{job_id}' not found"}
            return self._sanitize_job(job)

    def list_jobs(self) -> Dict[str, Any]:
        """List all scheduled jobs with status."""
        with self._lock:
            jobs = [self._sanitize_job(j) for j in self._jobs.values()]

        return {
            "total_jobs": len(jobs),
            "active_jobs": len([j for j in jobs if j.get("is_active")]),
            "paused_jobs": len([j for j in jobs if not j.get("is_active")]),
            "jobs": jobs,
            "scheduler_running": self._running,
            "available_presets": list(SchedulePreset.ALL.keys()),
        }

    def get_history(self, limit: int = 50, job_id: Optional[str] = None) -> Dict[str, Any]:
        """Get run history, optionally filtered by job_id."""
        with self._lock:
            history = list(self._history)

        if job_id:
            history = [h for h in history if h.get("job_id") == job_id]

        # Most recent first
        history.sort(key=lambda h: h.get("started_at", ""), reverse=True)

        return {
            "total_runs": len(history),
            "runs": history[:limit],
            "success_rate": self._compute_success_rate(history),
        }

    def trigger_now(self, job_id: str) -> Dict[str, Any]:
        """Manually trigger a job to run immediately (outside of schedule)."""
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return {"error": f"Job '{job_id}' not found"}

        return self._execute_job(job)

    # ──────────────────────────────────────────────
    # Background loop
    # ──────────────────────────────────────────────

    def _run_loop(self):
        """Main scheduler loop — checks jobs every 30 seconds."""
        while self._running:
            now = datetime.now(timezone.utc)

            with self._lock:
                jobs_to_run = [
                    j for j in self._jobs.values()
                    if j["is_active"] and j.get("next_run_at") and j["next_run_at"] <= now.isoformat()
                ]

            for job in jobs_to_run:
                try:
                    self._execute_job(job)
                except Exception as e:
                    logger.error(f"Scheduled job '{job['name']}' failed: {e}")
                    self._record_run(job["id"], "error", error=str(e))

            # ── Nightly expired-token cleanup ──
            # Runs once every 24 hours within this same background thread.
            # Rationale for scheduler vs check-on-read:
            #   - check-on-read only purges tokens for the requesting user;
            #     idle accounts accumulate rows indefinitely.
            #   - A separate Celery/APScheduler dep is unnecessary given this
            #     thread already ticks every 30s.
            #   - 24h cadence is appropriate: tokens expire after hours/days,
            #     so sub-minute precision is irrelevant.
            should_cleanup = (
                self._last_token_cleanup is None
                or (now - self._last_token_cleanup) >= timedelta(hours=24)
            )
            if should_cleanup:
                self._cleanup_expired_tokens()

            # Sleep 30 seconds between checks
            for _ in range(30):
                if not self._running:
                    break
                time.sleep(1)

    def _execute_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single ingestion job."""
        job_id = job["id"]
        started_at = datetime.now(timezone.utc)

        logger.info(f"Executing job: {job['name']} ({job_id})")

        try:
            # Import connector dynamically to avoid circular imports
            from app.connectors import get_connector  # type: ignore

            connector = get_connector(job["connector_type"], job["connector_config"])

            # Test connection first
            test_result = connector.test_connection()
            if test_result.get("status") != "ok":
                raise ConnectionError(f"Connection test failed: {test_result.get('message')}")

            # Extract data
            df = connector.extract()
            rows_extracted = len(df)

            # Run pipeline callback if provided
            pipeline_result = {}
            if job.get("pipeline_callback"):
                pipeline_result = job["pipeline_callback"](df)

            # Update job state
            with self._lock:
                if job_id in self._jobs:
                    self._jobs[job_id]["last_run_at"] = started_at.isoformat()
                    self._jobs[job_id]["last_status"] = "success"
                    self._jobs[job_id]["run_count"] += 1
                    self._jobs[job_id]["total_rows_ingested"] += rows_extracted
                    self._jobs[job_id]["next_run_at"] = self._compute_next_run(
                        self._jobs[job_id]["schedule_cron"]
                    )

            # Record run
            duration_ms = int((datetime.now(timezone.utc) - started_at).total_seconds() * 1000)
            self._record_run(
                job_id, "success",
                rows=rows_extracted,
                duration_ms=duration_ms,
                quality_score=pipeline_result.get("quality_score"),
            )

            return {
                "status": "success",
                "job_id": job_id,
                "rows_extracted": rows_extracted,
                "duration_ms": duration_ms,
                "pipeline_result": {k: v for k, v in pipeline_result.items() if k != "dataframe"},
            }

        except Exception as e:
            with self._lock:
                if job_id in self._jobs:
                    self._jobs[job_id]["last_status"] = "error"
                    self._jobs[job_id]["error_count"] += 1
                    self._jobs[job_id]["next_run_at"] = self._compute_next_run(
                        self._jobs[job_id]["schedule_cron"]
                    )

            duration_ms = int((datetime.now(timezone.utc) - started_at).total_seconds() * 1000)
            self._record_run(job_id, "error", error=str(e), duration_ms=duration_ms)

            return {"status": "error", "job_id": job_id, "error": str(e)}

    # ──────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────

    def _record_run(
        self, job_id: str, status: str,
        rows: int = 0, duration_ms: int = 0,
        quality_score: Optional[float] = None,
        error: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Record a run in history."""
        run = {
            "job_id": job_id,
            "status": status,
            "rows_extracted": rows,
            "duration_ms": duration_ms,
            "quality_score": quality_score,
            "error": error,
            "started_at": datetime.now(timezone.utc).isoformat(),
        }

        with self._lock:
            self._history.append(run)
            # Trim history
            if len(self._history) > self._max_history:
                self._history = self._history[-self._max_history:]

        return run

    def _cleanup_expired_tokens(self) -> None:
        """
        Delete RefreshToken rows whose expires_at timestamp is in the past.

        Uses a fresh DB session (not the request-scoped one) because this
        runs in a background thread outside any HTTP request lifecycle.
        The ix_refresh_token_expires_at index makes the WHERE clause O(log N)
        instead of a full-table scan.
        """
        try:
            from app.core.database import SessionLocal  # type: ignore
            from app.models.auth import RefreshToken  # type: ignore

            db = SessionLocal()
            try:
                cutoff = datetime.now(timezone.utc)
                deleted = (
                    db.query(RefreshToken)
                    .filter(RefreshToken.expires_at < cutoff)
                    .delete(synchronize_session=False)
                )
                db.commit()
                if deleted:
                    logger.info(
                        "[NEXUS] Token cleanup: deleted %d expired RefreshToken row(s)",
                        deleted,
                    )
                self._last_token_cleanup = cutoff
            finally:
                db.close()
        except Exception as exc:
            logger.error(
                "[NEXUS] Token cleanup failed: %s", exc, exc_info=True
            )

    def _compute_next_run(self, cron: str) -> str:
        """Compute next run time from a cron expression (simplified parser)."""
        now = datetime.now(timezone.utc)

        # Simple cron parsing for common patterns
        parts = cron.strip().split()
        if len(parts) != 5:
            # If not a valid cron, default to 1 hour from now
            return (now + timedelta(hours=1)).isoformat()

        minute, hour, dom, month, dow = parts

        # Handle simple patterns
        if minute.startswith("*/"):
            interval_min = int(minute[2:])
            next_minute = ((now.minute // interval_min) + 1) * interval_min
            if next_minute >= 60:
                return (now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)).isoformat()
            return now.replace(minute=next_minute, second=0, microsecond=0).isoformat()

        if hour.startswith("*/"):
            interval_hr = int(hour[2:])
            next_hour = ((now.hour // interval_hr) + 1) * interval_hr
            if next_hour >= 24:
                return (now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)).isoformat()
            return now.replace(hour=next_hour, minute=int(minute) if minute.isdigit() else 0, second=0, microsecond=0).isoformat()

        # Daily at specific time
        if minute.isdigit() and hour.isdigit() and dom == "*":
            target = now.replace(hour=int(hour), minute=int(minute), second=0, microsecond=0)
            if target <= now:
                target += timedelta(days=1)
            return target.isoformat()

        # Weekly
        if dow.isdigit():
            target_dow = int(dow)
            days_ahead = (target_dow - now.weekday()) % 7
            if days_ahead == 0 and now.hour >= int(hour if hour.isdigit() else "6"):
                days_ahead = 7
            target = (now + timedelta(days=days_ahead)).replace(
                hour=int(hour) if hour.isdigit() else 6,
                minute=int(minute) if minute.isdigit() else 0,
                second=0, microsecond=0,
            )
            return target.isoformat()

        # Monthly
        if dom.isdigit():
            target = now.replace(
                day=int(dom),
                hour=int(hour) if hour.isdigit() else 6,
                minute=int(minute) if minute.isdigit() else 0,
                second=0, microsecond=0,
            )
            if target <= now:
                # Move to next month
                if target.month == 12:
                    target = target.replace(year=target.year + 1, month=1)
                else:
                    target = target.replace(month=target.month + 1)
            return target.isoformat()

        # Default: 1 hour from now
        return (now + timedelta(hours=1)).isoformat()

    def _sanitize_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Remove internal fields (like callbacks) from job dict for API response."""
        return {k: v for k, v in job.items() if k != "pipeline_callback"}

    def _compute_success_rate(self, history: List[Dict]) -> float:
        """Calculate the success rate across all runs."""
        if not history:
            return 100.0
        successes = len([h for h in history if h.get("status") == "success"])
        return round(successes / len(history) * 100, 1)
