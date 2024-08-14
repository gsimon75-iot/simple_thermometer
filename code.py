import dht
import machine
import time
from umqtt.simple import MQTTClient

import config

# detach REPL if an uart pin is used for sensor
if config.dht_gpio in (1, -1, 3, -3):
    import os
    os.dupterm(None, 1)

mqtt = MQTTClient(
    client_id=config.mqtt_client_id,
    server=config.mqtt_server,
    user=config.mqtt_user,
    password=config.mqtt_password)

do_connect = True

sensor = dht.DHT22(machine.Pin(config.dht_gpio))

while True:
    time.sleep_ms(2000)

    print("measuring")
    try:
        sensor.measure()
    except Exception as e:
        print(f"measurement failed: {e.__class__} {e}")
        continue

    msg = f'{{"t": "{sensor.temperature()}", "h":"{sensor.humidity()}"}}'
    print(msg)

    if do_connect:
        try:
            mqtt.connect()
            do_connect = False
        except OSError as e:
            print(f"connection failed: {e}")
            continue

    try:
        mqtt.publish(config.mqtt_topic, msg.encode())
    except OSError as e:
        print(f"connection broken: {e}")
        do_connect = True


mqtt.disconnect()

# Test reception e.g. with:
# mosquitto_sub -t thermometer

