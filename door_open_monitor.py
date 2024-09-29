import asyncio
import os
from datetime import datetime

import paho.mqtt.client as mqtt

from services.ffmpeg import generate_video, remove_video, remove_old_videos
from services.gotify import send_gotify_message
from services.telegram import send_video

MQTT_HOST = os.getenv("MQTT_HOST")
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_TOPIC = os.getenv("MQTT_TOPIC")

send_gotify_message("Starting", "Starting ffmpeg_mqtt_listener.py")


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    client.subscribe(MQTT_TOPIC)
    send_gotify_message("Started",
                        f"Connected to mqtt server with result code {reason_code} and subscribed to topic {MQTT_TOPIC}")


def on_message(client, userdata, message):
    print(f"Received message: {message.payload}")
    if message.payload == b"open":
        print("Generating video...")
        try:
            filename = generate_video()
            asyncio.run(send_video(filename, f"Portão aberto!\nData: {datetime.now()}"))
            remove_video(filename)
            print("Message sent!")
        except Exception as exception:
            send_gotify_message("Error", f"Error generating video: {exception}")
            remove_old_videos()


mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

mqttc.connect(MQTT_HOST, 1883, 60)

try:
    remove_old_videos()
    mqttc.loop_forever()
except Exception as e:
    print(f"Error: {e}")
    send_gotify_message("Crash", f"Error: {e}")
