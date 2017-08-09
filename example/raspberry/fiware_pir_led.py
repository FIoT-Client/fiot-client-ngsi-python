import time
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
from iot import FiwareIotClient

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(11, GPIO.IN)     # read output from PIR motion sensor
GPIO.setup(3, GPIO.OUT)     # LED output pin

PIR_DEVICE_ID = "STELA_PIR"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("/4jggokgpepnvsb2uv4s40d59ov2/STELA_FAN/cmd")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + incoming_command)

    incoming_message = str(msg.payload)  # STELA_LED@change_state|ON

    cmd = incoming_message.split('@')[1]
    splitted_cmd = cmd.split('|')[0]
    cmd_name = splitted_cmd[0]
    cmd_param = splitted_cmd[1]

    if cmd_name == 'change_state':
        if cmd_param == 'ON':
            print('Change state to ON')
        elif cmd_param == 'OFF':
            print('Change state to OFF')
        else:
            print('Unknown parameter')

    elif cmd_name == 'change_speed':
        print('Change speed')

    else:
        print('Unknown command')


mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect("10.7.49.163", 1883, 60)

iot_client = FiwareIotClient("config.ini")
iot_client.set_service('STELAService', '/stela')

while True:
    presence = GPIO.input(11)
    iot_client.send_observation(PIR_DEVICE_ID, {'p': presence}, protocol='mqtt')

    if presence == 0:                   # when output from motion sensor is LOW
        print("No intruders", presence)
        GPIO.output(3, 0)               # turn OFF LED
    elif presence == 1:                 # when output from motion sensor is HIGH
        print("Intruder detected", presence)
        GPIO.output(3, 1)               # turn ON LED

    time.sleep(5)                       # wait for 5 seconds
