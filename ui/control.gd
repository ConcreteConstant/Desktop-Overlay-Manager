extends Control

@onready var opacity_slider := $VBoxContainer/HSlider

var client := StreamPeerTCP.new()
const HOST := "127.0.0.1"
const PORT := 51723

var initializing := true
var config := {}

func _ready():
	print("Connecting to Python IPC...")
	client.connect_to_host(HOST, PORT)
	opacity_slider.value_changed.connect(_on_opacity_changed)

func _process(_delta):
	client.poll()		# Required for Godot TCP to advance connection state
	
	if client.get_status() == StreamPeerTCP.STATUS_CONNECTED:
		if client.get_available_bytes() > 0:
			var data_buffer: PackedByteArray = client.get_data(client.get_available_bytes())[1]
			var json_string: String = data_buffer.get_string_from_utf8()
			
			var parsed_data = JSON.parse_string(json_string) # Use static method for simplicity
			
			if parsed_data is Dictionary or parsed_data is Array:
				# Successfully parsed JSON data
				print("Received JSON data: ", parsed_data)
				
				_handle_msg(parsed_data) #<------------ handle msg
				
			else:
				print("Failed to parse JSON string: ", json_string)
	elif client.get_status() == StreamPeerTCP.STATUS_ERROR:
		print("TCP connection error!")

func _handle_msg(msg):
	#print(msg)
	match msg["cmd"]:
		"init_config":
			initializing = true
			config = msg["config"]
			_apply_config_to_ui()
			initializing = false
		_:
			print("Unknown cmd:", msg)

func _apply_config_to_ui():
	opacity_slider.value = config.opacity * 100.0
	#interactive_checkbox.button_pressed = config.interactive

func _on_opacity_changed(value: float):
	if client.get_status() != StreamPeerTCP.STATUS_CONNECTED:
		return
	
	if initializing:
		return

	var msg = {
		"cmd": "set_opacity",
		"value": value / 100.0
	}

	var bytes := (JSON.stringify(msg) + "\n").to_utf8_buffer()
	client.put_data(bytes)

	print("Sent opacity:", value / 100.0)
