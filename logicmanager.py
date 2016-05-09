import time


class LogicManager:
    def __init__(self, min_dt=0.1):
        self._logic_handlers = []
        self._last_ts = 0
        self._min_dt = min_dt

    def add_logic(self, func):
        self._logic_handlers.append(func)

    def tick(self, **kwargs):
        now = time.time()
        if now - self._last_ts >= self._min_dt:
            self._last_ts = now
            for f in self._logic_handlers:
                f(now, **kwargs)


logic_manager = LogicManager()
