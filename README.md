# DiscordIPC-Emulator

A Python-based server implementation that communicates with Discord clients via IPC (Inter-Process Communication). This server can handle communication over a named pipe, send and receive JSON-encoded messages, and log the interactions for debugging and analysis.

## Features

- **Named Pipe Communication:** Establishes a named pipe (`\\.\pipe\discord-ipc-0`) to facilitate IPC communication between the server and Discord clients.
- **Message Handling:** Handles incoming requests and sends responses in JSON format.
- **Logging:** Logs incoming requests and outgoing responses to a file (`ipc_server.log`) for debugging and tracking.
- **Spoofed READY Event:** Sends a spoofed `READY` event with user and environment data to simulate a connection to the Discord API.

## Project Structure

- `DiscordIPCServer`: The main server class that manages the named pipe, communication, and logging.
  - **Named Pipe Creation:** The server creates a duplex pipe for bidirectional communication.
  - **Request Handling:** Reads incoming JSON requests from clients and logs them.
  - **Response Handling:** Sends spoofed responses (like the `READY` event) to clients.
  - **Logging:** Logs all requests and responses for debugging purposes.

## Requirements

- Python 3.9+
- Required Python libraries:
  - `pywin32`
  - `json`
  - `struct`
  - `logging`
  - `threading`
