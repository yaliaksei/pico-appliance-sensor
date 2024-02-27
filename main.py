from machine import Pin
import time
import urequests as requests
import network

# Initialize GPIO 16 as an input pin for the vibration sensor
vibration_sensor = Pin(16, Pin.IN)

# LED indicator
led = Pin("LED", Pin.OUT)

# flip flag
start_notification_flag = True
end_notification_flag = False

# loop pause
sleep_delay = 0.1

# 1 minutes monitor window
sensor_window = 1 * 60 * 10
sensor_events = [0] * sensor_window

# notification threshold within window
notification_threshold = 20

# connect to WiFi
ssid = "<WIFI-SID>"
password = "<WIFI-PASSWORD>"

# notification URL
# see https://ntfy.sh how to setup one
notification_url = "<notification_url>"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Continuously check the vibration sensor's state
while True:
    # If the sensor detects vibration (value is 1), print a message
    if vibration_sensor.value() == 1:
        
        # blink
        led.toggle()

        # every vibration cycle detected adds 1 into monitoring window
        # and pop out value from the other side of the list
        sensor_events.pop(0)
        sensor_events.append(1)

        print("Vibration detected! Total events " + str(sum(sensor_events)))

        # send notification if 
        if sum(sensor_events) > notification_threshold and start_notification_flag:
            print('Send start notification')
            requests.post(notification_url, data = "Washing cycle started!")
            start_notification_flag = False
            end_notification_flag = True

    # If no vibration is detected, print idle message
    else:
        print("...")

        # every silent cycle detected adds 0 into monitoring window
        # and pop out value from the other side of the list
        sensor_events.pop(0)
        sensor_events.append(0)

        # if no activity detected, send notification about washing program stop
        if sum(sensor_events) == 0 and end_notification_flag:
            print('Send end notification')
            requests.post(notification_url, data = "Washing cycle ended!")
            start_notification_flag = True
            end_notification_flag = False

    # Pause to lower the demand on the CPU
    time.sleep(sleep_delay)
