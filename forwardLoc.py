#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import paho.mqtt.enums as enums
import json
import subprocess

MQTT_HOST = ""
MQTT_PORT = 1884
MQTT_USERNAME = ""
MQTT_PASSWORD = "" 
TOPIC = ""
USE_TLS = False

def on_message(client, userdata, message):
    location = json.loads(message.payload)
   
    try:
        latitude = location["lat"]
        longitude = location["lon"]
        accuracy = location["acc"]
        altitude = location["alt"]
        altitude_accuracy = location["vac"]
        velocity = location["vel"]
        couse = location["cog"]

        # tell locsim to update location
        command = f"locsim start -x {latitude} -y {longitude} -h {accuracy} -a {altitude} -v {altitude_accuracy} -s {velocity} -c {couse}"
        print("Setting location...")
        subprocess.run(command.split(), text=True)

    except Exception as e:
        print(e)

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        client.subscribe(TOPIC)
    else:
        print(f"Failed to connect: Reason {reason_code}. Retrying...")

mqttc = mqtt.Client(enums.CallbackAPIVersion.VERSION2, client_id = "Forwarder", clean_session = True, transport="websockets")
mqttc.on_connect = on_connect
mqttc.on_message = on_message

if USE_TLS:
    mqttc.tls_set()

mqttc.username_pw_set(MQTT_USERNAME, password=MQTT_PASSWORD)
mqttc.connect(MQTT_HOST, MQTT_PORT)
mqttc.loop_forever()
