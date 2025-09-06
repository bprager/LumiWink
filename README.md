# LumiWink 👁✨

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi%20%7C%20ESP32-lightgrey.svg)
![Python](https://img.shields.io/badge/python-3.11+-yellow.svg)
![MQTT](https://img.shields.io/badge/MQTT-Mosquitto-success.svg)
![LLM](https://img.shields.io/badge/AI-Ollama%20backend-orange.svg)
![Voice](https://img.shields.io/badge/TTS-Piper-informational.svg)
![STT](https://img.shields.io/badge/STT-Vosk%20%7C%20Whisper-lightblue.svg)
![Hardware](https://img.shields.io/badge/3D--print-Ready-brightgreen.svg)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-ff69b4.svg)](CONTRIBUTING.md)

*A wink of light, a hint of life — your AI companion with presence.*

---

## What is LumiWink?

LumiWink is a **minimal embodied AI assistant**: part robotic presence, part psychological anchor, part conversation partner.
It lives as a **small eye-like device** that *looks at you, reacts to you, and expresses emotions* while speaking through a local AI brain.

Unlike voice-only assistants, LumiWink adds subtle **non-verbal cues** — blinks, nods, tilts, eyebrow arcs, aura glow, even a soft vibration “purr.”
The result is a **clearer, more fun, more human interaction** without needing humanoid complexity.

---

## Highlights

- 🎤 **Natural conversation** via **Ollama** backend (local or LAN LLMs).
- 👁 **Embodiment**: an eye with blinks, dilation, saccades, and eyebrow strips.
- 🎨 **Emotion overlays**: happy, amused, curious, annoyed, apologetic, calm, excited, and more.
- 🔊 **Voice pipeline**: wake word → STT → Ollama → TTS.
- 🧠 **State machine**: idle → attend → listen → think → speak → reflect → sleep.
- 🪞 **Psychological rituals**: morning greetings, focus guard, midday check-in, evening reflection.
- 🧭 **Gaze-follow**: tracks the speaker’s location and “looks” at them in real time.
- 🔒 **Privacy first**: no cloud, clear mic indicator, memory wipe, guest mode.
- ⚙️ **Modular**: Raspberry Pi as the *brain*, ESP32/Arduino as the *body*.

---

## Architecture at a Glance

```text
Voice ──► STT ──► Dialogue Router ──► Ollama ──► TTS ──► Speech Out
                   │                          │
                   └──► State Machine ◄── Vision (face, presence, gaze)
                               │
                      MQTT Event Bus
                               │
           ┌───────────────────┴───────────────────┐
           │                                       │
     ESP32/Arduino (Body)                  UI Modules (Eye, Aura)
    - Pan/tilt servos (gaze)             - Eye display (pupil, blinks)
    - Eyebrow LED bars                   - Aura strip (ambient mood)
    - LED ring / back-light              - Haptic feedback
```

> ✨ See [`docs/overview.md`](docs/overview.md) for PlantUML diagrams and detailed flows.

---

## Hardware (MVP)

- **Raspberry Pi 4/5** with camera + mic + speaker
- **ESP32 or Arduino Nano** with 2× micro servos
- **Round TFT/OLED** for eye
- **LED ring + eyebrow LED bars + aura strip**
- **3D printed shell + small pan-tilt mount**
- **Optional vibration motor / piezo buzzer**

---

## Quick Start

### 1. Setup Pi

```bash
sudo apt update
sudo apt install python3-pip mosquitto mosquitto-clients git -y
git clone https://github.com/<your_org>/lumiwink.git
cd lumiwink/software/pi/orchestrator
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Enable MQTT:

```bash
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
```

### 2. Connect Ollama

On your GPU host (or Pi if strong enough):

```bash
ollama pull gemma:2b-instruct
ollama serve
```

Edit `/etc/lumiwink.yaml`:

```yaml
ollama:
  host: http://odin:11434
  model: gemma:2b-instruct
  mode: chat
```

### 3. Run

```bash
python main.py
```

### 4. Flash Body Controller

Upload `software/arduino/lumenode/lumenode.ino` to your ESP32/Arduino and connect via USB.

---

## States & Emotions

- **Functional states**: idle, attend, listen, think, speak, reflect, sleep.
- **Emotion overlays**:

  - 😊 Happy — wide pupil, gentle nod, warm yellow aura.
  - 🤔 Curious — tilted head, raised brow, cyan glow.
  - 😲 Surprised — snap open eye, quick lift, white flash.
  - 😒 Annoyed — half lids, furrow, magenta aura, short buzz.
  - 🧘 Calm — slow breath, dim aqua aura.

Each emotion is **short-lived, preemptive, and decays back to neutral**.

---

## Roadmap

- ✅ MVP: voice loop, eye display, presence detection, Ollama replies.
- 🔜 Phase 2: eyebrow LEDs, aura glow, emotional overlays, gaze-follow.
- 🔮 Phase 3: diarization, affect mirroring, journaling, satellite “eyes.”

---

## Why LumiWink?

Because AI assistants should not feel like bland command lines.
They should have **a hint of life**, not through uncanny humanoids, but through **small expressive cues** that humans instantly understand.

LumiWink is:

- Minimal but **expressive**
- Playful but **private**
- Open, hackable, and **modular**

---

## Contributing

Contributions are welcome!

- Document MQTT topic contracts.
- Add emotion profiles (`configs/lumiwink.yaml`).
- Improve servo motion smoothing.
- Share your 3D printed shell variants.

See [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## License

MIT License. See [LICENSE](LICENSE).
