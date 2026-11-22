import time


class AlarmManager:
    """Small countdown helper. Tkinter owns the timer via root.after()."""

    def __init__(self):
        self.deadline = None
        self.alarm_id = None
        self.active = False

    def start(self, alarm_id: int, duration_seconds: int):
        self.alarm_id = alarm_id
        self.deadline = time.monotonic() + duration_seconds
        self.active = True

    def remaining_seconds(self) -> int:
        if not self.active or self.deadline is None:
            return 0
        return max(0, int(self.deadline - time.monotonic() + 0.999))

    def is_finished(self) -> bool:
        return self.active and self.deadline is not None and time.monotonic() >= self.deadline

    def clear(self):
        self.deadline = None
        self.alarm_id = None
        self.active = False
