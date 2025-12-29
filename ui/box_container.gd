extends Control

@export var input: LineEdit
@export var send_button: Button
@export var log: RichTextLabel

var client := StreamPeerTCP.new()
const HOST := "127.0.0.1"
const PORT := 51723

func _ready():
	log.bbcode_enabled = true

	send_button.pressed.connect(_on_send_pressed)
	log.add_text("Connecting to Python...\n")

	var err = client.connect_to_host(HOST, PORT)
	if err != OK:
		log.add_text("[ERROR] Could not connect\n")
		return

	client.set_no_delay(true)
	log.add_text("[OK] Connected\n")

func _process(_delta):
	client.poll()

	var status = client.get_status()

	if status == StreamPeerTCP.STATUS_CONNECTED:
		if client.get_available_bytes() > 0:
			var msg = client.get_utf8_string(client.get_available_bytes())
			log.add_text("Python: %s\n" % msg)

func _on_send_pressed():
	if client.get_status() != StreamPeerTCP.STATUS_CONNECTED:
		log.add_text("[ERROR] Not connected\n")
		return

	var text = input.text.strip_edges()
	if text.is_empty():
		print("NO TEXT")
		return
	
	print(text)
	client.put_utf8_string(text + "\n")
	log.add_text("Godot: %s\n" % text)
	input.clear()
