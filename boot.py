import machine
import sys
import gc
import webrepl
import network
import time

import config

def reload(mod):
  mod_name = mod.__name__
  gc.collect()
  del sys.modules[mod_name]
  gc.collect()
  return __import__(mod_name)


if config.wifi_led_gpio > 0:
    wifi_led = machine.Pin(config.wifi_led_gpio, machine.Pin.OUT, value=1)
    wifi_led_inverse = False
elif config.wifi_led_gpio < 0:
    wifi_led = machine.Pin(-config.wifi_led_gpio, machine.Pin.OUT, value=0)
    wifi_led_inverse = True
else:
    wifi_led = None
    wifi_led_inverse = False

print("switching to STA")
network.WLAN(network.AP_IF).active(False)
wlan = network.WLAN(network.STA_IF)
wlan.active(False)

print("connecting STA")
wlan.active(True)
wlan.connect(config.wifi_ssid, config.wifi_password)
for check in range(config.wifi_timeout_sec << 1):
    if wlan.isconnected():
        if wifi_led is not None:
            wifi_led.value(1 if wifi_led_inverse else 0)  # off
        break
    if wifi_led is not None:
        wifi_led.value(check & 1)
    time.sleep_ms(500)
else:
    print("failed STA, switching to AP")
    if wifi_led is not None:
        wifi_led.value(0 if wifi_led_inverse else 1)  # on
    wlan.active(False)
    wlan = network.WLAN(network.AP_IF)
    wlan.active(True)
    wlan.config(essid=config.wifi_ap_ssid, authmode=network.AUTH_OPEN)

print("network config:", wlan.ifconfig())

gc.collect()
webrepl.start()
gc.collect()

try:
    import code
except Exception as e:
    print(f"Failed to import code: {e}")
