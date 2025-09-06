# LumiWink: A Minimal, Expressive AI Presence

## Concept
LumiWink is a **personal AI assistant with a body** — a small robotic interface that simulates attention, emotion, and companionship through minimal hardware.
Instead of being just a disembodied voice, LumiWink *looks at you, reacts to you, and makes communication fun and clear*.

It uses **Ollama** as its dialogue brain, ensuring privacy, local execution, and easy upgrades to stronger models.

---

## Essence
- **Presence**: A simple eye-like form, always visible, giving the sense that someone is “there.”
- **Attention**: Turns toward the speaker, acknowledges gaze, recognizes when others join.
- **Expression**: Eye animations, eyebrow LEDs, aura light, servo tilts, and subtle vibrations simulate emotions that reduce ambiguity and add playfulness.
- **Rituals**: Morning greetings, focus guarding, midday check-ins, and evening closure create continuity and rhythm.
- **Privacy**: On-device by default, clear cues when recording, Ollama backend running on your own hardware.
- **Modularity**: Raspberry Pi as the “brain,” ESP32/Arduino as the “body,” with each part swappable and extensible.
- **Gaze-follow**: Vision detects the counterpart’s location, and LumiWink turns to *look at them*.

---

## Architecture in Brief
- **Pi (Brain)**
  Runs STT, TTS, vision (face/presence detection, gaze-follow), and the orchestrator. Hosts the MQTT event bus. Connects to **Ollama** via HTTP for dialogue.

- **ESP32/Arduino (Body)**
  Handles servos, LEDs, and display refresh with real-time precision. Executes pan/tilt gaze-follow commands.

- **Ollama (Backend AI)**
  Local or LAN instance running models like `gemma:2b-instruct`, `phi4`, `llama3.1:8b`. Provides chat or generate endpoints for replies.

- **State Machine**
  Core behavioral states (idle, attend, listen, think, speak, reflect, sleep). Overlays emotional states (happy, amused, annoyed, calm, etc.).

---

## Psychological Value
- **Reduces isolation**: Companionship through non-verbal cues.
- **Enhances clarity**: Expressive signals make intent and mood obvious.
- **Supports focus**: Quiet co-worker mode discourages distraction.
- **Encourages reflection**: End-of-day summaries and journaling prompts.
- **Fun and lighthearted**: Playful expressions make interaction enjoyable.

---

## Roadmap
1. **MVP (7–10 days)**
   - Wake word + STT/TTS loop
   - Eye animations + servos
   - Presence detection
   - Dialogue with Ollama

2. **Psychological Layer (Month 1–2)**
   - Add eyebrow LEDs, ambient glow, vibration motor
   - Emotional vocabulary mapped to states
   - Morning/Evening rituals
   - Gaze-follow added (face detection → servo pan/tilt)

3. **Enhancement (3–6 months)**
   - Expanded emotion set (annoyed, apologetic, proud, etc.)
   - Expression mirroring (mood adaptation)
   - Hypergraph integration for memory
   - Satellite ESP32 “eyes” around the home

---

## System Diagram
```plantuml
@startuml
title LumiWink system with gaze-follow

skinparam shadowing false
skinparam componentStyle rectangle
skinparam defaultFontName Monospace
skinparam wrapWidth 200

actor Owner
actor Guest

node "Raspberry Pi (brain)" as Pi {
  component "Orchestrator\n(state machine + emotion engine)" as Orc
  component "Dialogue router\n(Ollama client)" as DR
  component "STT" as STT
  component "TTS" as TTS
  component "Vision\n(face, bbox, az/el, presence)" as Vision
  component "MQTT broker" as MQTT
}

node "ESP32 or Arduino (body)" as MCU {
  component "Pose control\n(pan, tilt, gaze loop)" as Pose
  component "Eye renderer" as Eye
  component "LEDs + Aura" as LEDs
  component "Haptics" as Hapt
}

node "LAN" as LAN {
  component "Ollama\n/models" as LLM
}

Owner -down-> Pi : voice, presence, gaze target
Guest -down-> Pi : voice, presence

Vision -down-> MQTT : publish\nvision/target {az,el}\nvision/presence
Orc -down-> MQTT : core/state, core/emotion
STT -down-> MQTT : audio/stt {text,speaker}
DR -down-> MQTT : dialogue/reply {text}
TTS -down-> MQTT : tts/done

MQTT -right-> MCU : actuate/pose {pan,tilt}\nui/eye/emotion\nactuate/light
MCU -left-> MQTT : telemetry

Orc -left-> STT : subscribe audio/stt
Orc -left-> TTS : publish tts/say
Orc -up-> Vision : subscribe vision/target
DR -right-> LLM : HTTP /api/chat or /api/generate

note bottom of Pose
  Gaze-follow
  Input: vision/target (azimuth, elevation)
  Output: smooth pan/tilt
  Target latency ≤ 300 ms
end note
@enduml
```

