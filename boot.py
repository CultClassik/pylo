import esp
import machine
import time
import ubinascii
import webrepl
import network
from machine import Pin
from umqtt.simple import MQTTClient
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

	webrepl.start()
	
	# Set up the power led sensor gpio pin
	pin_sensor()
	
	# wait X seconds before connecting to mqtt broker to ensure we're good to go with wifi connection
	print("Preparing to connect to MQTT broker..")
	time.sleep(3)
	
	mqtt_go()


def mqtt_go():
	global client
	print('Connecting to {} as {}'.format(CONFIG['mqtt']['broker'], CONFIG['mqtt']['client_id']))
	client = MQTTClient(CONFIG['mqtt']['client_id'], CONFIG['mqtt']['broker'])
	client.DEBUG = True
	client.set_callback(mqtt_command)
	client.set_last_will(CONFIG['mqtt']['topic_status'], 'offline', True, 0)
	client.connect(clean_session=True)
	
	state = None
	
	try:
		# Publish the device status 
		print('Publishing ONLINE to topic: {}'.format(CONFIG['mqtt']['topic_status']))
		client.publish(CONFIG['mqtt']['topic_status'], "online")
		# Publish the pc power state
		state = mqtt_status(CONFIG['mqtt']['topic_state'])
		print('Publishing {} to topic: {}'.format(state, CONFIG['mqtt']['topic_state']))
		client.publish(CONFIG['mqtt']['topic_state'], state)
	except:
		print("Error on INIT")

	client.subscribe(CONFIG['mqtt']['topic_cmd'])
	
	# Loop forever go to work, lots of error checking needed to handle broker outages
	while True:
		# If the pc power state has changed, publish it
		if not state == mqtt_status(CONFIG['mqtt']['topic_state']):
			#print('State changed from {} to {}'.format(state, mqtt_status(CONFIG['mqtt']['topic_state'])))
			try:
				state = mqtt_status(CONFIG['mqtt']['topic_state'])
				print("Publishing {} to topic: {}".format(state, CONFIG['mqtt']['topic_state']))
				client.publish(CONFIG['mqtt']['topic_state'], state, True, 0)
			except:
				print("Error publishing power state")
			
		try:
			print("Checking for messages..")
			client.check_msg()
		except:
			print("Error on SUBSCRIBE")
			time.sleep(4)
			mqtt_conn()
		else:
			time.sleep(1)

	client.disconnect()

	
def mqtt_conn(clean_session=False):
	time.sleep(3)
	try:
		client.connect(clean_session)
	except:
		print("Error on conn")
	else:
		client.subscribe(CONFIG['mqtt']['topic_cmd'])


def mqtt_status(topic, message=None):
	if message == None:
		# read power led status from pc with gpio here
		pwr_status = sensor_pin.value()
	
		if pwr_status == 0:
			msg = "ON"
		else:
			msg = "OFF"
	
	# Return the power status, optionally to be used by calling code
	return msg
	
	
def mqtt_command(topic, message):
	msg = message.decode()
	print('Received message {} on topic {}'.format(msg, topic.decode()))
	pin = None
	
	if msg == "RESET":
		pin = machine.Pin(CONFIG['gpio']['reset_sw'], machine.Pin.OUT)
		print("Sending reset.")
	elif (msg == "ON") or (msg == "OFF"):
		print("Sending power {}".format(msg))
		pin = machine.Pin(CONFIG['gpio']['power_sw'], machine.Pin.OUT)
	else:
		print("Unknown command, ignoring.")
	
	if not pin == None:
		pin.value(1)
		time.sleep(2)
		pin.value(0)
		state = mqtt_status(CONFIG['mqtt']['topic_state'])
		client.publish(CONFIG['mqtt']['topic_state'], state)
		return state
	else:
		return pin

def pin_sensor():
	global sensor_pin
	sensor_pin = Pin(CONFIG['gpio']['power_led'], Pin.IN, Pin.PULL_UP)

	
if __name__ == '__main__':
	import esp
	esp.osdebug(None)
	startup()
