"""TCP receiver for a configurable sliding-window file-transfer exercise."""

import os
import random
import socket

HOST = "127.0.0.1"
PORT = 12345
CONFIG_FILE = "config.txt"


def read_config(filename: str = CONFIG_FILE) -> dict[str, str]:
    """Load colon-separated settings stored beside this script."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    config: dict[str, str] = {}

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            config[key.strip()] = value.strip().strip('"').strip("'")
    return config


def start_server() -> None:
    """Accept packets and acknowledge correctly ordered data chunks."""
    config = read_config()
    max_message_size = int(config.get("maximum_msg_size", "100"))
    drop_probability = float(config.get("drop_prob", "0.0"))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        print(f"[SERVER] Listening on {HOST}:{PORT} (drop rate: {drop_probability})")

        while True:
            connection, address = server_socket.accept()
            print(f"[SERVER] Connected to {address}")
            handle_connection(connection, max_message_size, drop_probability)


def handle_connection(
    connection: socket.socket, max_message_size: int, drop_probability: float
) -> None:
    """Handle handshake, size negotiation, and sequential acknowledgements."""
    expected_sequence = 0
    buffer = ""

    with connection:
        while True:
            data = connection.recv(1024).decode()
            if not data:
                return
            buffer += data

            if "SIN" in buffer:
                connection.sendall(b"SIN/ACK")
                buffer = buffer.replace("SIN", "", 1)
            if "ACK" in buffer and "M" not in buffer:
                buffer = buffer.replace("ACK", "", 1).strip()
            if "SIZE_REQ" in buffer:
                connection.sendall(str(max_message_size).encode())
                buffer = buffer.replace("SIZE_REQ", "", 1)

            while buffer.startswith("M") and ":" in buffer:
                header, payload = buffer.split(":", 1)
                if len(payload) < max_message_size:
                    break

                buffer = payload[max_message_size:]
                sequence_number = int(header[1:])
                if random.random() < drop_probability:
                    print(f"[SERVER] Intentionally dropped packet {header}")
                    continue

                if sequence_number == expected_sequence:
                    expected_sequence += 1
                connection.sendall(f"ACK{expected_sequence - 1}".encode())


if __name__ == "__main__":
    start_server()
