client_id = "nm01"

CONFIG = {
	"wifi": {
		"essid": "ssidGoesHere",
		"password": "wifiPasswordHere"
	},
	"mqtt": {
		"broker": "mqtt.broker.name",
		"client_id": client_id,
		"topic_cmd": 'pylo/{}/cmd'.format(client_id),
		"topic_state": 'pylo/{}/state'.format(client_id),
		"topic_status": 'pylo/{}/status'.format(client_id),
	},
	"gpio": {
		"power_led": 4,
		"power_sw": 5,
		"reset_sw": 16
	}
}
