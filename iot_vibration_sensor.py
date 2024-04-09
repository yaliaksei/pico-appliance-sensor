from machine import Pin
import utime
import network
from umqtt.simple import MQTTClient

vibration_sensor = Pin(17, Pin.IN)
led = Pin("LED", Pin.OUT)
led.off()

sleep_delay = 0.1

# connect to WiFi
ssid = "WIFI_SSID"
password = "WIFI_PASSWORD"

# AWS ThingName
CLIENT_ID = b'IOT_CLIENT_ID'
# AWS Endpoint
AWS_ENDPOINT = b'AWS_ENDPOINT'

# AWS IoT Core publish topic
PUB_TOPIC = b'/' + CLIENT_ID + '/vibration'

            
# Reading Thing Private Key and Certificate into variables for later use
with open('/certs/key.der', 'rb') as f:
    DEV_KEY = f.read()
# Thing Certificate
with open('/certs/cert.der', 'rb') as f:
    DEV_CRT = f.read()
    
def wifi_connect():
    print("Connecting to wifi...")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        led.on()
        print("Waiting for connection...")
        time.sleep(0.5)
        led.off()
        time.sleep(0.5)
    print("Connection details: " + str(wlan.ifconfig()))

wifi_connect()

# Set AWS IoT Core connection details
mqtt = MQTTClient(
    client_id=CLIENT_ID,
    server=AWS_ENDPOINT,
    port=8883,
    keepalive=5000,
    ssl=True,
    ssl_params={'key':DEV_KEY, 'cert':DEV_CRT, 'server_side':False})

# Establish connection to AWS IoT Core
mqtt.connect()

while True:
    if vibration_sensor.value() == 1:
        print('Vibration detected')
        led.value(1)
        message = '{"vibration": "on"}'
        # QoS Note: 0=Sent zero or more times, 1=Sent at least one, wait for PUBACK
        # See https://docs.aws.amazon.com/iot/latest/developerguide/mqtt.html
        mqtt.publish(topic=PUB_TOPIC, msg=message, qos=0)
        utime.sleep(sleep_delay)
    else:
        print('No vibration')
        led.value(0)
        utime.sleep(sleep_delay)
            



