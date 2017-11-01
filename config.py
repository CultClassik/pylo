client_id = "IDforUseWithMqtt"
CONFIG = {
	"wifi": {
		"essid": "WifiNetworkSSIDhere",
		"password": "obvi"
	},
	"mqtt": {
		"broker": "IPorNameOfMqttBroker",
		"client_id": bytes(client_id, "ascii"),
		"topic_sub": b"pylo/" + client_id + "/cmd",
		"topic_pub": b"pylo/" + client_id + "/status"
	},
	"gpio": {
		"power_led": 4,
		"power_sw": 5,
		"reset_sw": 16
	}
}
