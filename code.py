import dht
import machine
import time
from umqtt.simple import MQTTClient

import config

dht = dht.DHT22(machine.Pin(config.dht_gpio))

mqtt = MQTTClient(
    client_id=config.mqtt_client_id,
    server=config.mqtt_server,
    user=config.mqtt_user,
    password=config.mqtt_password)

do_connect = True


while True:
    time.sleep_ms(2000)

    print("measuring")
    dht.measure()

    msg = f'{{"t": "{dht.temperature()}", "h":"{dht.humidity()}"}}'
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

