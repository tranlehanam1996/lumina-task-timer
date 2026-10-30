"""Pure, dependency-free Pomodoro timer state machine.

This module contains the core timing logic used by Lumina Task Timer. Keeping it
free of any GUI dependency makes it easy to unit test and reuse from other
front ends (CLI, web, etc.).
"""

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Dict


class SessionType(Enum):
    WORK = "work"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"


@dataclass
class TimerConfig:
    """Configuration for a Pomodoro cycle."""

    work_minutes: int = 25
    short_break_minutes: int = 5
    long_break_minutes: int = 15
    sessions_until_long_break: int = 4

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        for name in ("work_minutes", "short_break_minutes", "long_break_minutes"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if (
            not isinstance(self.sessions_until_long_break, int)
            or isinstance(self.sessions_until_long_break, bool)
            or self.sessions_until_long_break < 1
        ):
            raise ValueError("sessions_until_long_break must be a positive integer")


class PomodoroTimer:
    """A small state machine describing one Pomodoro timer instance."""

    def __init__(self, config: TimerConfig = None):
        self.config = config if config is not None else TimerConfig()
        self.config.validate()
        self.session_type = SessionType.WORK
        self.remaining_seconds = self.config.work_minutes * 60
        self.completed_work_sessions = 0
        self.is_running = False
        self.is_paused = False

    @property
    def total_seconds(self) -> int:
        if self.session_type is SessionType.WORK:
            return self.config.work_minutes * 60
        if self.session_type is SessionType.SHORT_BREAK:
            return self.config.short_break_minutes * 60
        return self.config.long_break_minutes * 60

    def start(self) -> None:
        """Start or resume the timer."""
        self.is_paused = False
        self.is_running = True

    def pause(self) -> None:
        """Pause a running timer."""
        if self.is_running:
            self.is_paused = True
            self.is_running = False

    def reset(self) -> None:
        """Reset to the beginning of a fresh work session."""
        self.is_running = False
        self.is_paused = False
        self.session_type = SessionType.WORK
        self.remaining_seconds = self.config.work_minutes * 60
        self.completed_work_sessions = 0

    def tick(self) -> bool:
        """Advance the timer by one second.

        Returns True when the current session just completed.
        """
        if not self.is_running or self.is_paused:
            return False
        if self.remaining_seconds <= 0:
            self.remaining_seconds = 0
            return self._complete_session()
        self.remaining_seconds -= 1
        if self.remaining_seconds <= 0:
            return self._complete_session()
        return False

    def advance(self, seconds: int) -> int:
        """Advance the timer by the given number of seconds.

        Returns the number of sessions completed during the advance. A paused or
        stopped timer is left unchanged.
        """
        if (
            not isinstance(seconds, int)
            or isinstance(seconds, bool)
            or seconds < 0
        ):
            raise ValueError("seconds must be a non-negative integer")
        if not self.is_running or self.is_paused:
            return 0
        completed = 0
        for _ in range(seconds):
            if self.tick():
                completed += 1
                if not self.is_running:
                    break
        return completed

    def _complete_session(self) -> bool:
        if self.session_type is SessionType.WORK:
            self.completed_work_sessions += 1
            if (
                self.completed_work_sessions
                % self.config.sessions_until_long_break
                == 0
            ):
                self.session_type = SessionType.LONG_BREAK
            else:
                self.session_type = SessionType.SHORT_BREAK
        else:
            self.session_type = SessionType.WORK
        self.remaining_seconds = self.total_seconds
        self.is_running = False
        self.is_paused = False
        return True

    def progress(self) -> float:
        """Fraction of the current session that has elapsed (0.0 - 1.0)."""
        total = self.total_seconds
        if total <= 0:
            return 0.0
        remaining = self.remaining_seconds
        if remaining < 0:
            remaining = 0
        elif remaining > total:
            remaining = total
        return (total - remaining) / total

    def to_dict(self) -> Dict[str, Any]:
        return {
            "config": asdict(self.config),
            "session_type": self.session_type.value,
            "remaining_seconds": self.remaining_seconds,
            "completed_work_sessions": self.completed_work_sessions,
            "is_running": self.is_running,
            "is_paused": self.is_paused,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PomodoroTimer":
        if not isinstance(data, dict):
            raise ValueError("timer state must be a mapping")

        raw_config = data.get("config", {})
        if raw_config is None:
            raw_config = {}
        if not isinstance(raw_config, dict):
            raise ValueError("config must be a mapping")
        try:
            timer = cls(TimerConfig(**raw_config))
        except (TypeError, ValueError) as exc:
            raise ValueError("invalid timer config") from exc

        raw_session_type = data.get("session_type", SessionType.WORK.value)
        try:
            if isinstance(raw_session_type, SessionType):
                timer.session_type = raw_session_type
            else:
                timer.session_type = SessionType(raw_session_type)
        except (TypeError, ValueError) as exc:
            raise ValueError("invalid session_type") from exc

        raw_remaining = data.get("remaining_seconds", timer.total_seconds)
        if isinstance(raw_remaining, bool) or not isinstance(raw_remaining, int):
            try:
                raw_remaining = int(raw_remaining)
            except (TypeError, ValueError) as exc:
                raise ValueError("remaining_seconds must be an integer") from exc
        if raw_remaining < 0:
            raw_remaining = 0
        if raw_remaining > timer.total_seconds:
            raw_remaining = timer.total_seconds
        timer.remaining_seconds = raw_remaining

        raw_completed = data.get("completed_work_sessions", 0)
        if isinstance(raw_completed, bool) or not isinstance(raw_completed, int):
            try:
                raw_completed = int(raw_completed)
            except (TypeError, ValueError) as exc:
                raise ValueError("completed_work_sessions must be an integer") from exc
        if raw_completed < 0:
            raw_completed = 0
        timer.completed_work_sessions = raw_completed

        is_paused = bool(data.get("is_paused", False))
        timer.is_paused = is_paused
        timer.is_running = bool(data.get("is_running", False)) and not is_paused
        return timer
