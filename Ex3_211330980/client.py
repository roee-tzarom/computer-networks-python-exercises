import socket


def read_config(filename):
    config = {}
    try:
        with open(filename, 'r') as file:
            for line in file:
                if ':' in line:
                    key, value = line.split(':', 1)
                    config[key.strip()] = value.strip()
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
    return config


def start_client():
    config = read_config('input.txt')
    server_ip = '127.0.0.1'
    server_port = 12345

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((server_ip, server_port))

        # --- HANDSHAKE START ---
        # 1. Send 'SIN'
        print("[CLIENT] Sending SIN...")
        client_socket.send("SIN".encode())

        # 2. Receive 'SIN/ACK'
        data = client_socket.recv(1024).decode()
        if data == "SIN/ACK":
            print("[CLIENT] Received SIN/ACK. Sending ACK...")

            # 3. Send 'ACK'
            client_socket.send("ACK".encode())
            print("[CLIENT] Handshake successful!")

            # (Logic for sending data will go here later)

        else:
            print(f"[CLIENT] Handshake failed. Received: {data}")

    except Exception as e:
        print(f"[CLIENT] Error: {e}")
    finally:
        client_socket.close()


if __name__ == "__main__":
    start_client()