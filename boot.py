import esp
import machine
import time
import ubinascii
import webrepl
import network
from machine import Pin
from config import CONFIG

def startup():
	# config wifi
	sta_if = network.WLAN(network.STA_IF)
	if not sta_if.isconnected():
		print("Connecting to WiFi..")
		sta_if.active(True)
		sta_if.connect("NumberOfTheThing", "C0ng0B0ng0!")
		while not sta_if.isconnected():
			pass
			
	time.sleep(2)

	dev_id = ubinascii.hexlify(machine.unique_id()).decode()
	mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()

	# print stuff to console
	print("Device: " + dev_id)
	print("MAC Address: " + mac)
	print('WiFi config:', sta_if.ifconfig())

	# start the webrepl
	webrepl.start()
	
	# connect to the mq
	mqtt_go(CONFIG)

def mqtt_go(CONFIG):
	from umqtt.robust import MQTTClient
	client = MQTTClient(CONFIG['mqtt']['client_id'], CONFIG['mqtt']['broker'])
	print("Connected to {}".format(CONFIG['mqtt']['broker']))
	client.DEBUG = True
	client.set_callback(mqtt_command)
	client.connect()
	print ("Subscribing to topic: " + CONFIG['mqtt']['topic_sub'].decode())
	client.subscribe(CONFIG['mqtt']['topic_sub'])
	# Set up the power led sensor gpio pin
	pin_sensor(CONFIG['gpio']['power_led'])
	# Loop forever and work it
	while True:
		# Publish power status
		mqtt_status(client, CONFIG['mqtt']['topic_pub'])
		# Check for commands published to this device in mqtt
		client.check_msg()
		time.sleep(3)
	
	client.disconnect()

def mqtt_status(client, topic):
	# read power led status from pc with gpio here
	my_status = sensor_pin.value()
	print ("Publishing " + str(my_status) + " to topic: " + topic.decode())
	client.publish(topic, bytes(my_status))
	
def mqtt_command(topic, msg):
	print("mqtt message received")
	print(topic, '::', msg)

def pin_sensor(my_pin):
	global sensor_pin
	sensor_pin = Pin(my_pin, Pin.IN, Pin.PULL_UP)

def gpio_ctl(pin):
	# still need to implement gpio outputs to optocouplers to manipulate pc power and reset buttons
	return False
	
	
if __name__ == '__main__':
	import esp
	esp.osdebug(None)
	startup()
	