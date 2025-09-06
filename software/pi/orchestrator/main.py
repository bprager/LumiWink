"""LumiWink Orchestrator

Implements the core state machine + emotion dispatch described in:
 - docs/architecture.md
 - docs/PRD.md

Responsibilities:
 - Subscribe to MQTT topics (audio/awake, audio/stt, dialogue/reply, tts/done, vision/target, vision/presence)
 - Maintain coherent state transitions (idle→attend→listen→think→speak→reflect→idle)
 - Relay dialogue replies to TTS
 - Forward gaze targets to actuator topics
 - Emit emotional overlays based on events (wake, reply, idle timeout)

This initial implementation uses paho-mqtt (add to dependencies) and a
lightweight synchronous loop; can be evolved to asyncio if needed later.
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

try:
    import paho.mqtt.client as mqtt  # type: ignore
except ImportError:  # pragma: no cover
    mqtt = None  # type: ignore

from .emotion_rules import EmotionEngine

# ---------------------------------------------------------------------------
# Configuration loading
# ---------------------------------------------------------------------------

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "configs" / "lumiwink.yaml"


def load_config(path: Optional[Path] = None) -> Dict[str, Any]:
    p = path or DEFAULT_CONFIG_PATH
    if yaml and p.exists():
        with p.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


# ---------------------------------------------------------------------------
# State machine
# ---------------------------------------------------------------------------

VALID_STATES = [
    "idle",
    "attend",
    "listen",
    "think",
    "speak",
    "reflect",
    "sleep",
]


@dataclass
class OrchestratorState:
    name: str = "idle"
    last_transition: float = time.time()
    last_user_activity: float = time.time()
    current_reply_id: Optional[str] = None


class Orchestrator:
    def __init__(self, client, config: Dict[str, Any]):
        self.client = client
        self.config = config
        self.state = OrchestratorState()
        self._lock = threading.RLock()
        self.emo = EmotionEngine(self.publish, config)
        self._stop = threading.Event()
        # TTL tick for emotions
        self._emotion_timer = threading.Thread(
            target=self._emotion_watchdog, daemon=True
        )
        self._emotion_timer.start()

    # ---------------------- MQTT helpers ---------------------------------
    def publish(self, topic: str, payload: Dict[str, Any]):
        msg = json.dumps(payload, ensure_ascii=False)
        self.client.publish(topic, msg, qos=0, retain=False)

    # ---------------------- State management -----------------------------
    def set_state(self, new_state: str):
        if new_state not in VALID_STATES:
            return
        with self._lock:
            if new_state == self.state.name:
                return
            prev = self.state.name
            self.state.name = new_state
            self.state.last_transition = time.time()
            self.publish("core/state", {"state": new_state, "prev": prev})
            if new_state == "attend":
                self.emo.emit("surprised", 0.9, 900)
            elif new_state == "speak":
                self.emo.emit("happy", 0.6)

    # ---------------------- Event handlers -------------------------------
    def on_wake(self):
        self.set_state("attend")
        self.publish("actuate/light", {"mode": "attend", "intensity": 0.6})
        self.state.last_user_activity = time.time()

    def on_stt(self, text: str, speaker: Optional[str] = None):
        self.set_state("listen")
        self.state.last_user_activity = time.time()
        # Forward to dialogue router
        self.publish("dialogue/query", {"text": text, "speaker": speaker})
        self.set_state("think")

    def on_dialogue_reply(self, text: str):
        # Move to speak, hand to TTS
        self.set_state("speak")
        self.publish("tts/say", {"text": text})

    def on_tts_done(self):
        # Optionally reflect or go idle
        self.set_state("reflect")
        # Minimal reflection delay
        threading.Timer(0.6, lambda: self.set_state("idle")).start()

    def on_presence(self, count: int):
        # Basic presence trigger: if zero for a while, maybe sleep
        if count == 0 and self.state.name == "idle":
            # Sleep after inactivity threshold
            if time.time() - self.state.last_user_activity > 300:
                self.set_state("sleep")
        elif count > 0 and self.state.name == "sleep":
            self.set_state("idle")

    def on_gaze_target(self, az: float, el: float):
        # Clamp / sanity check values (-90..90 pan, -45..45 tilt typical)
        az = max(-90.0, min(90.0, az))
        el = max(-45.0, min(45.0, el))
        self.publish("actuate/pose", {"pan": az, "tilt": el})

    # ---------------------- Emotion TTL watchdog -------------------------
    def _emotion_watchdog(self):
        # Called periodically; emotion_rules has no internal timers so we simulate TTL end.
        # A more robust approach would track TTL expiry timestamps per active emotion.
        ACTIVE_TTL_MS = 1500  # fallback neutral TTL
        while not self._stop.is_set():
            time.sleep(0.2)
            now = time.time()
            if self.emo.active:
                started = self.emo.last.get(self.emo.active["name"], now)
                ttl_ms = self.emo.active.get("ttl_ms", ACTIVE_TTL_MS)
                if (now - started) * 1000 >= ttl_ms:
                    self.emo.on_ttl_end()

    # ---------------------- Idle tasks -----------------------------------
    def periodic(self):
        # Called from main loop
        if self.state.name == "idle":
            # Soft heartbeat emotion occasionally
            if int(time.time()) % 30 == 0:
                self.emo.emit("calm", 0.4, 1200)

    # ---------------------- Dispatcher -----------------------------------
    def handle_mqtt(self, topic: str, payload: Dict[str, Any]):
        if topic == AUDIO_AWAKE:
            self.on_wake()
        elif topic == AUDIO_STT:
            self.on_stt(payload.get("text", ""), payload.get("speaker"))
        elif topic == DIALOGUE_REPLY:
            self.on_dialogue_reply(payload.get("text", ""))
        elif topic == TTS_DONE:
            self.on_tts_done()
        elif topic == VISION_PRESENCE:
            self.on_presence(int(payload.get("count", 0)))
        elif topic == VISION_TARGET:
            az_raw: Any = payload.get("az")
            el_raw: Any = payload.get("el")
            if az_raw is None or el_raw is None:
                return
            try:
                az_f = float(az_raw)  # type: ignore[arg-type]
                el_f = float(el_raw)  # type: ignore[arg-type]
            except (TypeError, ValueError):
                return
            self.on_gaze_target(az_f, el_f)

    # ---------------------- Shutdown -------------------------------------
    def stop(self):
        self._stop.set()


# ---------------------------------------------------------------------------
# MQTT wiring
# ---------------------------------------------------------------------------


def build_mqtt_client(
    orchestrator: Orchestrator, host: str = "localhost", port: int = 1883
):
    if mqtt is None:
        raise RuntimeError("paho-mqtt not installed; add 'paho-mqtt' to dependencies")
    client = mqtt.Client()

    def on_connect(client, _userdata, _flags, _rc):  # type: ignore
        subs = [
            (AUDIO_AWAKE, 0),
            (AUDIO_STT, 0),
            (DIALOGUE_REPLY, 0),
            (TTS_DONE, 0),
            (VISION_PRESENCE, 0),
            (VISION_TARGET, 0),
        ]
        for t, q in subs:
            client.subscribe(t, qos=q)

    def on_message(_client, _userdata, msg):  # type: ignore
        try:
            payload = json.loads(msg.payload.decode("utf-8")) if msg.payload else {}
        except json.JSONDecodeError:
            payload = {}
        orchestrator.handle_mqtt(msg.topic, payload)

    client.on_connect = on_connect  # type: ignore
    client.on_message = on_message  # type: ignore
    client.connect(host, port, keepalive=30)
    return client


# ---------------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------------


def run(orchestrator: Orchestrator, client):
    client.loop_start()
    try:
        while True:
            orchestrator.periodic()
            time.sleep(0.2)
    except KeyboardInterrupt:
        pass
    finally:
        orchestrator.stop()
        client.loop_stop()


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="LumiWink Orchestrator")
    p.add_argument(
        "--config", type=Path, help="Path to lumiwink.yaml", default=DEFAULT_CONFIG_PATH
    )
    p.add_argument("--mqtt-host", default="localhost")
    p.add_argument("--mqtt-port", type=int, default=1883)
    p.add_argument(
        "--demo",
        action="store_true",
        help="Run a short synthetic demo without real MQTT inputs",
    )
    return p.parse_args(argv)


def demo_sequence(o: Orchestrator):
    o.handle_mqtt(AUDIO_AWAKE, {})
    o.handle_mqtt(AUDIO_STT, {"text": "What's the weather?"})
    time.sleep(0.3)
    o.handle_mqtt(DIALOGUE_REPLY, {"text": "Looks sunny with a gentle breeze."})
    time.sleep(0.3)
    o.handle_mqtt(TTS_DONE, {})
    # Simulate a gaze target update
    o.handle_mqtt(VISION_TARGET, {"az": 15.0, "el": 2.0})


def main(argv=None):  # pragma: no cover
    args = parse_args(argv)
    config = load_config(args.config)
    # Dummy client if demo without paho
    # Build orchestrator with dummy or real MQTT client
    if args.demo:

        class DummyClient:
            def publish(self, topic, payload, _qos=0, _retain=False):  # type: ignore
                # Demo mode: just print outbound messages
                print(f"PUB {topic}: {payload}")

            def loop_start(self):  # no-op for demo
                return None

            def loop_stop(self):  # no-op for demo
                return None

        client = DummyClient()
        orchestrator = Orchestrator(client, config)
        demo_sequence(orchestrator)
        time.sleep(1.2)
    else:
        if mqtt is None:
            print(
                "paho-mqtt missing. Install with: pip install paho-mqtt",
                file=sys.stderr,
            )
            return 1
        dummy_client = mqtt.Client()
        orchestrator = Orchestrator(dummy_client, config)
        client = build_mqtt_client(orchestrator, args.mqtt_host, args.mqtt_port)
        run(orchestrator, client)
    return 0


## Topic constants
AUDIO_AWAKE = "audio/awake"
AUDIO_STT = "audio/stt"
DIALOGUE_REPLY = "dialogue/reply"
TTS_DONE = "tts/done"
VISION_PRESENCE = "vision/presence"
VISION_TARGET = "vision/target"


if __name__ == "__main__":
    main(sys.argv[1:])
