import json
import math
import time

import paho.mqtt.client as mqtt

# This stub only logs parameter mapping for the eye renderer.
# Replace prints with your TFT draw calls.

def map_eye(emotion):
    name = emotion.get("name","neutral")
    inten = float(emotion.get("intensity",0.6))
    if name == "excited":
        return {"pupil_size": 0.85*inten, "pulse_hz": 1.6, "blink_rate": 0.18}
    if name == "amused":
        return {"pupil_size": 0.7, "pulse_hz": 0.8, "blink_style": "wink"}
    if name == "annoyed":
        return {"pupil_size": 0.3, "blink_rate": 0.05, "lid": "half"}
    if name == "surprised":
        return {"pupil_size": 1.0, "pulse_hz": 0.0, "blink_rate": 0.0}
    if name == "focused":
        return {"pupil_size": 0.35, "blink_rate": 0.06}
    return {"pupil_size": 0.5, "blink_rate": 0.1}

def on_message(_c,_u,msg):
    em = json.loads(msg.payload.decode())
    params = map_eye(em)
    print("[EYE]", em["name"], params)

if __name__ == "__main__":
    client = mqtt.Client()
    client.connect("127.0.0.1",1883,60)
    client.on_message = on_message
    client.subscribe("core/emotion")
    client.loop_forever()

