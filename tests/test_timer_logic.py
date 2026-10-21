import unittest

from timer_logic import PomodoroTimer, TimerConfig, SessionType


class TestTimerConfig(unittest.TestCase):
    def test_defaults(self):
        cfg = TimerConfig()
        self.assertEqual(cfg.work_minutes, 25)
        self.assertEqual(cfg.short_break_minutes, 5)
        self.assertEqual(cfg.long_break_minutes, 15)
        self.assertEqual(cfg.sessions_until_long_break, 4)

    def test_invalid_config(self):
        with self.assertRaises(ValueError):
            TimerConfig(work_minutes=0).validate()
        with self.assertRaises(ValueError):
            TimerConfig(sessions_until_long_break=0).validate()


class TestPomodoroTimer(unittest.TestCase):
    def test_initial_state(self):
        t = PomodoroTimer(TimerConfig(work_minutes=1, short_break_minutes=1, long_break_minutes=2))
        self.assertEqual(t.session_type, SessionType.WORK)
        self.assertEqual(t.remaining_seconds, 60)
        self.assertFalse(t.is_running)

    def test_tick_completes_session(self):
        t = PomodoroTimer(TimerConfig(work_minutes=1, short_break_minutes=1, long_break_minutes=2))
        t.start()
        for _ in range(59):
            self.assertFalse(t.tick())
        self.assertTrue(t.tick())
        self.assertEqual(t.session_type, SessionType.SHORT_BREAK)
        self.assertEqual(t.completed_work_sessions, 1)
        self.assertFalse(t.is_running)

    def test_long_break_after_four_sessions(self):
        t = PomodoroTimer(
            TimerConfig(work_minutes=1, short_break_minutes=1, long_break_minutes=2, sessions_until_long_break=4)
        )
        for _ in range(4):
            t.start()
            for _ in range(60):
                t.tick()
            t.start()
            for _ in range(t.total_seconds):
                t.tick()
        self.assertEqual(t.completed_work_sessions, 4)

    def test_pause_and_resume(self):
        t = PomodoroTimer(TimerConfig(work_minutes=1))
        t.start()
        t.tick()
        before = t.remaining_seconds
        t.pause()
        self.assertTrue(t.is_paused)
        self.assertFalse(t.is_running)
        self.assertFalse(t.tick())
        self.assertEqual(t.remaining_seconds, before)
        t.start()
        self.assertTrue(t.is_running)
        self.assertFalse(t.is_paused)

    def test_reset(self):
        t = PomodoroTimer(TimerConfig(work_minutes=1))
        t.start()
        for _ in range(30):
            t.tick()
        t.reset()
        self.assertEqual(t.remaining_seconds, 60)
        self.assertEqual(t.completed_work_sessions, 0)
        self.assertEqual(t.session_type, SessionType.WORK)
        self.assertFalse(t.is_running)

    def test_progress(self):
        t = PomodoroTimer(TimerConfig(work_minutes=2))
        t.start()
        for _ in range(60):
            t.tick()
        self.assertAlmostEqual(t.progress(), 0.5, places=5)

    def test_serialization_roundtrip(self):
        t = PomodoroTimer(TimerConfig(work_minutes=1, short_break_minutes=1, long_break_minutes=2))
        t.start()
        for _ in range(30):
            t.tick()
        data = t.to_dict()
        restored = PomodoroTimer.from_dict(data)
        self.assertEqual(restored.remaining_seconds, t.remaining_seconds)
        self.assertEqual(restored.session_type, t.session_type)
        self.assertEqual(restored.completed_work_sessions, t.completed_work_sessions)


if __name__ == "__main__":
    unittest.main()
