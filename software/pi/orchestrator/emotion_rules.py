import time
from collections import deque

PRIORITY = [
    "surprised",
    "apologetic",
    "annoyed",
    "proud",
    "excited",
    "happy",
    "encouraging",
    "curious",
    "concerned",
    "confident",
    "focused",
    "calm",
    "neutral",
]


class EmotionEngine:
    def __init__(self, publish, cfg):
        self.publish = publish
        self.cfg = cfg or {}
        self.active = None
        self.last = {}
        self.queue = deque()

    def can_fire(self, name):
        limit = (self.cfg.get("rate_limits") or {}).get(name, {})
        min_interval = limit.get("min_interval_ms", 0) / 1000.0
        last_t = self.last.get(name, 0)
        return (time.time() - last_t) >= min_interval

    def emit(self, name, intensity=0.7, ttl_ms=None):
        if not self.can_fire(name):
            return
        prof = (self.cfg.get("emotion_profiles") or {}).get(name, {})
        ttl = ttl_ms if ttl_ms is not None else prof.get("ttl_ms", 2000)
        msg = {"name": name, "intensity": float(intensity), "ttl_ms": int(ttl)}
        self._maybe_preempt(msg)

    def _maybe_preempt(self, msg):
        if self.active:
            cur = self.active["name"]
            if PRIORITY.index(msg["name"]) < PRIORITY.index(cur):
                self.queue.appendleft(self.active)
                self._activate(msg)
            else:
                self.queue.append(msg)
        else:
            self._activate(msg)

    def _activate(self, msg):
        self.active = msg
        self.last[msg["name"]] = time.time()
        self.publish("core/emotion", msg)

    def on_ttl_end(self):
        self.active = None
        if self.queue:
            self._activate(self.queue.popleft())
        else:
            self.publish(
                "core/emotion", {"name": "neutral", "intensity": 0.5, "ttl_ms": 1500}
            )
