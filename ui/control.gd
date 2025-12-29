extends Control

@onready var slider := $VBoxContainer/HSlider

var client := StreamPeerTCP.new()
const HOST := "127.0.0.1"
const PORT := 51723

func _ready():
	print("Connecting to Python IPC...")
	client.connect_to_host(HOST, PORT)
	slider.value_changed.connect(_on_opacity_changed)

func _process(_delta):
	# Required for Godot TCP to advance connection state
	client.poll()

func _on_opacity_changed(value: float):
	if client.get_status() != StreamPeerTCP.STATUS_CONNECTED:
		return

	var msg = {
		"cmd": "set_opacity",
		"value": value / 100.0
	}

	var bytes := (JSON.stringify(msg) + "\n").to_utf8_buffer()
	client.put_data(bytes)

	print("Sent opacity:", value / 100.0)
