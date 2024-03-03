# Simple asynchronous server for Pico W
import network
import socket
from time import sleep
from machine import Pin
from picozero import pico_temp_sensor, pico_led
import urequests as requests

# Use board led as notification
led = Pin("LED", Pin.OUT)

# Initialize GPIO 16 as an input pin for the vibration sensor
vibration_sensor = Pin(16, Pin.IN)

ssid = "B441-WiFi"
password = "Summer2021!"

notification_url = "https://ntfy.sh/aliakseisery-alerts"

# flip flag
start_notification_flag = True
end_notification_flag = False

# loop pause
sleep_delay = 0.1

# 1 minute monitor window
sensor_window = 1 * 60 * 10
sensor_events = [0] * sensor_window

# notification threshold within window
notification_threshold = 20

def sensor_listener():
    # Continuously check the vibration sensor's state
    while True:
        # If the sensor detects vibration (value is 1), print a message
        if vibration_sensor.value() == 1:
            
            # led on
            led.value(1)

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

            # led off
            led.value(0)

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
        sleep(sleep_delay)

def connect():
    # Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    while(wlan.isconnected() == False):
        print('Waiting for connection..')
        sleep(1)
    
    # Return obtained IP
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    
    return ip

def open_socket(ip):
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    
    return connection

def status_page(temperature, state):
    # Template HTML
    html = f"""
            <!DOCTYPE html>
            <html>
            <form action="./lighton">
            <input type="submit" value="Light on" />
            </form>
            <form action="./lightoff">
            <input type="submit" value="Light off" />
            </form>
            <p>LED is {state}</p>
            <p>Temperature is {temperature}</p>
            </body>
            </html>
            """
    
    return str(html)

def serve(connection):
    state = 'OFF'
    temperature = 0
    
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        
        try:
            request = request.split()[1]
        except IndexError:
            pass
        if request == '/lighton?':
            pico_led.on()
            state = 'ON'
        elif request =='/lightoff?':
            pico_led.off()
            state = 'OFF'
            
        temperature = pico_temp_sensor.temp
        
        html = status_page(temperature, state)
        client.send(html)
        client.close()
    
try:
    ip = connect()
    sensor_listener()
    #connection = open_socket(ip)
    #serve(connection)
except KeyboardInterrupt:
    machine.reset()

