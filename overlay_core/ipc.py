import json
import socket
import threading

class IPCServer:
    def __init__(self, manager, host="127.0.0.1", port=51723):
        self.manager = manager
        self.host = host
        self.port = port
        self.running = True

    def start(self):
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()

    def _run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen(1)
            print(f"[IPC] Listening on {self.host}:{self.port}")
            while self.running:
                conn, addr = s.accept()
                print(f"[IPC] Connected from {addr}")

                with conn:
                    file = conn.makefile("r")
                    for line in file:
                        print(f"[IPC] Received raw: {line.strip()}")
                        self._handle(line.strip(), conn)

                print("[IPC] Connection closed")

    def _send(self, conn, msg):
        conn.sendall((json.dumps(msg) + "\n").encode())

    def _handle(self, raw, conn):
        # raw = raw.lstrip("\x00# \t\r\n")
        print("[IPC] _handle raw:", repr(raw))

        try:
            cmd = json.loads(raw)
        except Exception as e:
            print("[IPC] JSON ERROR:", e)
            return
        
        print("[IPC] Parsed:", cmd)

        name = cmd.get("cmd")
        if name == "set_opacity":
            print("IPC: set_opacity", cmd["value"])
            self.manager.set_opacity(cmd["value"])
        
