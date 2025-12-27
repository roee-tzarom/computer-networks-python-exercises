import socket


# --- Function to read configuration ---
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


def start_server():
    # Load configuration
    config = read_config('input.txt')
    server_port = 12345

    # Create TCP Socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', server_port))
    server_socket.listen(1)

    print(f"[SERVER] Listening on port {server_port}...")

    while True:
        conn, addr = server_socket.accept()
        print(f"[SERVER] Connected to {addr}")

        # --- HANDSHAKE START ---
        try:
            # 1. Wait for 'SIN'
            data = conn.recv(1024).decode()
            if data == "SIN":
                print("[SERVER] Received SIN. Sending SIN/ACK...")

                # 2. Send 'SIN/ACK'
                conn.send("SIN/ACK".encode())

                # 3. Wait for 'ACK'
                data = conn.recv(1024).decode()
                if data == "ACK":
                    print("[SERVER] Handshake successful!")

                    # (Logic for receiving data will go here later)

                else:
                    print(f"[SERVER] Error: Expected ACK, got {data}")
            else:
                print(f"[SERVER] Error: Expected SIN, got {data}")

        except Exception as e:
            print(f"[SERVER] Error: {e}")

        conn.close()
        print("[SERVER] Connection closed.\n")


if __name__ == "__main__":
    start_server()