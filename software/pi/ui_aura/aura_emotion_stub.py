import json

import paho.mqtt.client as mqtt


def hsv_for(name):
    table = {
      "happy": (50, 0.9, 0.9),
      "excited": (25, 1.0, 1.0),
      "amused": (20, 0.8, 0.8),
      "curious": (180, 0.7, 0.7),
      "focused": (210, 0.6, 0.5),
      "concerned": (30, 0.8, 0.6),
      "annoyed": (315, 0.8, 0.5),
      "apologetic": (220, 0.4, 0.4),
      "calm": (190, 0.4, 0.3),
      "neutral": (0, 0.0, 0.6)
    }
    return table.get(name, table["neutral"])

def on_message(_c,_u,msg):
    em = json.loads(msg.payload.decode())
    print("[AURA]", em["name"], hsv_for(em["name"]))

if __name__ == "__main__":
    c = mqtt.Client()
    c.connect("127.0.0.1",1883,60)
    c.on_message = on_message
    c.subscribe("core/emotion")
    c.loop_forever()

