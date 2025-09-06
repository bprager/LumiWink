import json

import paho.mqtt.client as mqtt


def on_message(_c, _u, msg):
    em = json.loads(msg.payload.decode())
    name = em.get("name", "neutral")
    pattern = {
        "excited": "tick_double",
        "happy": "purr_soft",
        "annoyed": "buzz_short",
        "surprised": "click",
        "encouraging": "tick",
    }.get(name, None)
    if pattern:
        print("[HAPTIC]", name, pattern)


if __name__ == "__main__":
    c = mqtt.Client()
    c.connect("127.0.0.1", 1883, 60)
    c.on_message = on_message
    c.subscribe("core/emotion")
    c.loop_forever()
