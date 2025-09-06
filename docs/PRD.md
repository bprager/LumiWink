Perfect addition — that’s the **gaze-following requirement** we already hinted at with face detection, but let’s make it explicit in the PRD. Below is the updated section with the new requirement integrated cleanly.

---

# Product Requirements Document (PRD)

**Project Name:** LumiWink
**Tagline:** *A wink of light, a hint of life — your AI companion with presence.*
**Version:** 1.2
**Date:** 2025-09-05

---

## 1. Purpose

LumiWink is a **minimal embodied AI assistant** that creates the illusion of presence, attention, and emotional expression. Unlike voice-only assistants, LumiWink uses visual, motion, and auditory cues to make interactions more human-like, clear, and fun — while ensuring privacy through **local-first AI with Ollama**.

---

## 2. Goals & Non-Goals

### Goals

* Provide **natural, concise voice interaction** using Ollama as dialogue backend.
* Create a **physical presence** through a minimal “eye” form with subtle animations.
* Express a **broad range of simulated emotions** (happy, amused, curious, annoyed, etc.) with minimal hardware.
* Support **psychological rituals**: morning greeting, deep work guard, midday check-in, evening reflection.
* Remain **modular**: Pi (brain) + ESP32/Arduino (body).
* Prioritize **privacy**: all inference runs on local hardware, no cloud dependency.
* **Gaze awareness**: detect the **location of the counterpart** and follow their direction, so LumiWink appears to *look* at the person speaking.

### Non-Goals (for MVP)

* Full humanoid embodiment (arms, mouth, realistic face).
* Long or rambling conversations (default is concise).
* Cloud-only integrations.
* Direct control of smart home devices (phase 2+ only).

---

## 3. User Stories

1. **As an owner**, I say the wake word → LumiWink looks at me, listens, and answers via Ollama.
2. **As an owner**, when I move across the room → LumiWink rotates its “eye” to follow me.
3. **As an owner**, when I look up during deep work → LumiWink acknowledges me silently, but doesn’t distract.
4. **As an owner**, when someone else joins → LumiWink turns toward them briefly, greets neutrally, then returns focus to me.
5. **As an owner**, after a break → LumiWink welcomes me back and offers to resume where I left off.
6. **As an owner**, at day’s end → LumiWink summarizes my day and prompts me for a short reflection.
7. **As a guest**, I can interact briefly with LumiWink → it rotates toward me politely but avoids personal memory.

---

## 4. Key Features

### Core Interaction

* Wake word detection (on-device).
* Speech-to-text (STT) via Vosk or Whisper (offload optional).
* Dialogue routing to Ollama (local or LAN).
* Text-to-speech (TTS) via Piper.
* State machine (idle → attend → listen → think → speak → reflect → sleep).

### Visual & Emotional Expression

* **Eye display (TFT/OLED)**: pupil dilation, blinks, saccades.
* **Eyebrow LED bars**: arc, furrow, asymmetry → strong emotion signals.
* **Aura LED strip**: ambient back-glow for mood.
* **Servo gimbal**: pan, tilt, nod, shake, **gaze-follow** toward speaker.
* **Vibration motor or piezo**: subtle tactile/sound feedback.
* **Emotion overlays**: amused, excited, annoyed, apologetic, calm, etc.

### Psychological Layer

* Morning greeting and priority prompt.
* Focus/flow mode (minimal distraction).
* Midday encouragement and fatigue sensing.
* Evening reflection summary.

### Privacy & Security

* Clear recording light when mic is active.
* Memory toggle and wipe command.
* Guest mode disables personalization.
* Ollama backend runs locally — no cloud required.

---

## 5. Architecture

### Brain (Raspberry Pi)

* Runs orchestrator, STT, TTS, vision, emotion engine.
* Publishes events via MQTT.
* Forwards queries to Ollama backend.
* **Vision module computes face bounding boxes + azimuth/elevation → orchestrator → servo gimbal.**

### Body (ESP32/Arduino)

* Drives servos, LEDs, eye display, haptics.
* Subscribes to MQTT topics (`actuate/pose`, `ui/eye/emotion`, etc.).
* **Executes pan/tilt commands to simulate gaze.**
* Handles real-time motion loops.

### Backend AI (Ollama)

* LAN instance (e.g., RTX GPU host).
* Exposed via REST API.
* Configurable models: `gemma:2b-instruct`, `phi4`, `llama3.1:8b`.
* Default: concise, witty persona.

---

## 6. Functional Requirements

### 6.1 Speech Pipeline

* Detect wake word reliably (false wake < 1/hr).
* STT latency < 1.0s for short utterances.
* Ollama query → response within 1–2s for compact models.
* TTS begins < 500ms after response received.

### 6.2 Emotion Engine

* Supports priority preemption (e.g., *surprised* interrupts *neutral*).
* Each emotion has TTL + decay back to neutral.
* Rate-limits rare states (e.g., *annoyed* ≤ 1/min).

### 6.3 Visual & Motion Rendering

* Eye FPS ≥ 20 Hz.
* Servo movements smooth (<5° jitter).
* Aura color transitions <200 ms ramp.
* **Face tracking and gaze-follow latency ≤ 300 ms** from detection to servo update.

### 6.4 Privacy

* Guest mode auto-triggers when unknown voice dominant.
* Wipe memory command executed within 2s.
* Recording light synced with VAD activity.

---

## 7. Success Metrics

* **Interaction latency**: full loop (speech → Ollama → TTS) ≤ 2.5s.
* **Wake word accuracy**: >95% detection in quiet room.
* **Expression clarity**: >80% recognition rate in user tests (Happy vs Annoyed vs Surprised).
* **Gaze-follow accuracy**: servo orientation within ±10° of user position 90% of the time.
* **User engagement**: daily use ≥ 2 interactions per session.
* **Trust**: positive user feedback on privacy and transparency.

---

## 8. Roadmap

### Phase 1 (MVP, 2 weeks)

* Core state machine, eye display, servos, STT/TTS loop.
* Ollama integration for dialogue.
* Presence detection.

### Phase 2 (Month 1–2)

* Emotion overlays (happy, amused, excited, calm).
* Eyebrow LEDs + aura back-glow.
* Morning/evening rituals.
* **Add gaze-follow (servo pan/tilt tied to detected face location).**

### Phase 3 (Month 3–6)

* Expanded emotion set (annoyed, apologetic, proud, etc.).
* Expression mirroring (basic affect recognition).
* Hypergraph integration (contextual memory).
* Satellite ESP32 “eyes” across rooms.

---

