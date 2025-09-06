# LumiWink states and emotion overlays

## Functional states
idle, attend, listen, think, speak, reflect, sleep

| State   | Enter on                             | Exit on                                 | Cues                                   |
|---------|--------------------------------------|------------------------------------------|----------------------------------------|
| idle    | boot, inactivity timeout             | wake word, face near with eye contact    | soft breath, rare blinks               |
| attend  | wake word, new speaker focus         | user begins speaking                     | brighten, orient, slight nod           |
| listen  | VAD active, diarized owner           | end of speech, timeout                   | still gaze, low motion                 |
| think   | text ready, LLM pending              | TTS ready                                | micro saccades, calm light             |
| speak   | TTS playing                          | end of audio                             | subtle head motion, animated pupil     |
| reflect | end of session or evening window     | user response, timeout                   | short summary, one line prompt         |
| sleep   | nightly schedule, manual command     | morning window, wake word, movement      | eye close animation, low power         |

Rules
- Unknown speaker: greet briefly, return focus to owner.
- Guest mode: suppress personalization, presence only.
- Safety light when capturing audio.

## Emotion overlays
One active at a time. Applied on top of any functional state. Short decay back to neutral.

| Emotion     | Typical trigger                              | Eye                          | Eyebrows                | Servo micro motion           | Aura color              | Haptic or sound   | Default duration |
|-------------|-----------------------------------------------|------------------------------|-------------------------|------------------------------|-------------------------|-------------------|------------------|
| neutral     | default, after decay                          | steady pupil, rare blink     | flat                    | none                         | soft white             | none              | persistent       |
| happy       | praise, success, friendly greeting            | wider pupil, smooth blink    | high gentle arc         | tiny nods                    | warm yellow            | soft purr         | 3 s              |
| amused      | witty reply, playful banter                   | half blink, quick wink       | asymmetric up           | head tilt right              | peach                  | light tick        | 2 s              |
| excited     | user enthusiasm, start action                 | rapid dilation pulses        | high arc, slight bounce | quick nods                   | bright orange          | double tick       | 2 s              |
| curious     | ambiguous request, unknown person detected    | slow saccades                | one eyebrow up          | slow tilt left or right      | cyan                   | none              | 3 s              |
| confident   | clear answer, task ready                      | steady focused pupil         | slight down tilt        | small forward lean           | teal                   | none              | 2 s              |
| proud       | milestone reached                             | slow dilation, sparkle blink | high arc held           | single nod                   | gold                   | soft purr         | 2 s              |
| focused     | deep work mode                                | small pupil, fewer blinks    | slight down tilt        | minimal motion               | cool blue              | none              | holds            |
| concerned   | user frustration detected                     | micro saccades, tight pupil  | inward tilt, light furrow| small retract                | amber                  | short buzz        | 2 s              |
| annoyed     | repeated interrupts, noisy room               | half lids, small pupil       | sharp inward tilt       | small head shake             | magenta                | short double buzz | 1.5 s            |
| surprised   | sudden event, wake word in silence            | snap open, fast dilate       | quick high raise        | slight lift                  | white flash then neutral| click            | 0.8 s            |
| apologetic  | misheard, error                               | half lids, slow blink        | shallow down arc        | small downward tilt          | dim blue               | none              | 2 s              |
| encouraging | hesitation sensed, return from break          | soft dilate, warm blink      | gentle high arc         | small forward nod            | lime                   | soft tick         | 3 s              |
| calm        | wind down, evening                            | slow breath loop             | relaxed flat            | none                         | dim aqua               | none              | scene            |

Notes
- Annoyed is rare. Cap to one instance per minute.
- Night hours use dim cool tones. No buzz.

## MQTT topics
- Publish emotion
  - topic: `core/emotion`
    payload: `{ "name": "amused", "intensity": 0.7, "ttl_ms": 2000 }`
- Renderers subscribe and map to parameters
  - `ui/eye/emotion`, `ui/brow/emotion`, `ui/aura/emotion`, `actuate/pose/emotion`, `haptic/pattern`

## Priority and blending
Priority high to low: surprised, apologetic, annoyed, proud, excited, happy, encouraging, curious, concerned, confident, focused, calm, neutral.

Only one overlay is active. Higher priority preempts. Ramp in 150 to 250 ms. Hold for ttl. Decay to neutral in 400 to 800 ms.

## Orchestrator hints
- On wake from silence: fire surprised, then attend.
- On repeated ASR error: apologetic, then encouraging.
- On positive sentiment in reply: happy or proud, based on task tag.
- Unknown dominant speaker: curious at low intensity.
- Deep work: focused scene, suppress flashy overlays.

