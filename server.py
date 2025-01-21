import win32pipe
import win32file
import json
import struct
import threading
import logging

class DiscordIPCServer:
    PIPE_NAME = r'\\.\pipe\discord-ipc-0'

    def __init__(self):
        self.running = True
        self.setup_logging()

    def setup_logging(self):
        """Set up logging to log received messages to a file."""
        logging.basicConfig(
            filename='ipc_server.log',
            level=logging.INFO,
            format='%(asctime)s - %(message)s'
        )

    def start_server(self):
        print(f"Starting Discord IPC server on {self.PIPE_NAME}")
        while self.running:
            try:
                hPipe = self.create_pipe()
                print(f"Server waiting for connection on pipe {self.PIPE_NAME}")
                win32pipe.ConnectNamedPipe(hPipe, None)
                print(f"Server connected to pipe {self.PIPE_NAME}")

                self.handle_client(hPipe)
                win32file.CloseHandle(hPipe)

            except Exception as e:
                print(f"Error: {e}")

    def create_pipe(self):
        """Create a named pipe."""
        return win32pipe.CreateNamedPipe(
            self.PIPE_NAME,
            win32pipe.PIPE_ACCESS_DUPLEX,
            win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
            win32pipe.PIPE_UNLIMITED_INSTANCES,
            512, 512, 0, None
        )

    def handle_client(self, hPipe):
        """Handle communication with a connected client."""
        self.send_ready_event(hPipe)

        while self.running:
            request_data = self.read_request(hPipe)
            if request_data:
                self.log_request(request_data)  # Log the incoming request
            else:
                break

    def send_ready_event(self, hPipe):
        """Send a ready event to the client."""
        response_data = {
            "cmd": "DISPATCH",
            "data": {
                "v": 1,
                "config": {
                    "cdn_host": "cdn.discordapp.com",
                    "api_endpoint": "//discord.com/api",
                    "environment": "production"
                },
                "user": {
                    "id": "IDDD", #Spoofed DiscordID
                    "username": "USER", #Spoofed DiscordUsername
                    "discriminator": "0",
                    "global_name": "XX", #Spoofed GName
                    "avatar": "XX", #Spoofed Avatar
                    "avatar_decoration_data": None,
                    "bot": False,
                    "flags": 288,
                    "premium_type": 0
                }
            },
            "evt": "READY",
            "nonce": None
        }

        self.send_response(hPipe, response_data)

    def send_response(self, hPipe, response_data):
        """Send a response to the client."""
        response_json = json.dumps(response_data, indent=4)
        response_bytes = response_json.encode('utf-8')
        header = struct.pack('<II', 1, len(response_bytes))
        win32file.WriteFile(hPipe, header + response_bytes)
        self.log_response(response_data)

    def read_request(self, hPipe):
        """Read incoming request data from the pipe."""
        try:
            header = win32file.ReadFile(hPipe, 8)
            op_code, length = struct.unpack('<II', header[1])  # Unpack the header

            # Now read the data
            request_data = win32file.ReadFile(hPipe, length)[1]
            return json.loads(request_data.decode('utf-8'))  # JSON data
        except Exception as e:
            print(f"Failed to read request: {e}")
            return None

    def log_request(self, request_data):
        """Log the received request data."""
        logging.info("Received request:\n%s", json.dumps(request_data, indent=4))

    def log_response(self, response_data):
        """Log the sent response data."""
        logging.info("Sent response:\n%s", json.dumps(response_data, indent=4))

    def stop_server(self):
        """Stop the IPC server."""
        print("Stopping Discord IPC server...")
        self.running = False

if __name__ == "__main__":
    server = DiscordIPCServer()

    try:
        server_thread = threading.Thread(target=server.start_server)
        server_thread.start()
    except KeyboardInterrupt:
        server.stop_server()
