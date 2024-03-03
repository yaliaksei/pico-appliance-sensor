from machine import Pin
import time
import urequests as requests
import network
import socket

# Initialize GPIO 16 as an input pin for the vibration sensor
vibration_sensor = Pin(16, Pin.IN)

# LED indicator
led = Pin("LED", Pin.OUT)

# flip flag
start_notification_flag = True
end_notification_flag = False

sleep_delay = 0.1

# 1 minute activity window initialized with '0'
activity_window_size = 1 * 60 * 10
activity_window = [0] * activity_window_size

# 15 minutes silence window initialized with '1'
silence_window_size = 15 * 60 * 10
silence_window = [1] * silence_window

# notification threshold
notification_threshold = 20

# connect to WiFi
ssid = 'SSID'
password = 'PASSWORD'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Continuously check the vibration sensor's state
while True:
    # If the sensor detects vibration (value is 1), update activity and silence windows
    if vibration_sensor.value() == 1:
        
        # turn led on
        led.value(1)

        # every vibration detected adds 1 into window
        activity_window.pop(0)
        activity_window.append(1)
        
        # also, update silence window
        silence_window.pop(0)
        silence_window.append(1)

        print("Vibration detected! Total events " + str(sum(activity_window)))

        # send notification if 
        if sum(activity_window) > notification_threshold and start_notification_flag:
            print('Cycle started..')
            print('Send start notification')
            requests.post("https://ntfy.sh/<actual_url>", data = "Washing cycle started!")
            start_notification_flag = False
            end_notification_flag = True

    # If no vibration is detected, print idle message
    else:
        print("No vibration. Total vibration events " + str(sum(activity_window)))
        
        # turn led off
        led.value(0)

        activity_window.pop(0)
        activity_window.append(0)
        
        # also, update silence window
        silence_window.pop(0)
        silence_window.append(0)

        # if no activity detected, send notification about washing program stop
        if sum(silence_window) < 5 and end_notification_flag:
            print('Cycle ended..')
            print('Send end notification')
            requests.post("https://ntfy.sh/<actual_url>", data = "Washing cycle ended!")
            start_notification_flag = True
            end_notification_flag = False

    # Pause to lower the demand on the CPU
    time.sleep(sleep_delay)
