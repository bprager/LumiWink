import json

import paho.mqtt.client as mqtt

SHAPES = {
  "high_arc":[8,7,6,5,4,3,2,1],
  "asym_up":[0,1,2,3,4,6,7,7],
  "furrow":[2,3,4,6,6,4,3,2],
  "flat":[4,4,4,4,4,4,4,4]
}

def map_brow(name):
    if name == "excited": return "high_arc"
    if name == "amused": return "asym_up"
    if name == "annoyed": return "furrow"
    return "flat"

def on_message(_c,_u,msg):
    em = json.loads(msg.payload.decode())
    shape = SHAPES.get(map_brow(em["name"]), SHAPES["flat"])
    print("[BROW]", em["name"], shape)

if __name__ == "__main__":
    c = mqtt.Client()
    c.connect("127.0.0.1",1883,60)
    c.on_message = on_message
    c.subscribe("core/emotion")
    c.loop_forever()

