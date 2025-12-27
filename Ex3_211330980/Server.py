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


def start_server():
    config = read_config('input.txt')
    max_msg_size = int(config.get('maximum_msg_size', '100'))

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # תיקון לשגיאת פורט תפוס
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('127.0.0.1', 12345))
    server_socket.listen(1)

    print(f"[SERVER] Listening...")

    while True:
        conn, addr = server_socket.accept()
        expected_seq = 0
        buffer = ""

        try:
            while True:
                data = conn.recv(1024).decode()
                if not data: break
                buffer += data

                # 1. Handshake
                if "SIN" in buffer:
                    conn.send("SIN/ACK".encode())
                    buffer = buffer.replace("SIN", "")

                # --- התיקון הקריטי: ניקוי ה-ACK של הלחיצת יד ---
                if "ACK" in buffer and "M" not in buffer:
                    buffer = buffer.replace("ACK", "").replace("\n", "").strip()
                # -----------------------------------------------

                # 2. Size Negotiation
                if "SIZE_REQ" in buffer:
                    conn.send(str(max_msg_size).encode())
                    buffer = buffer.replace("SIZE_REQ", "")

                # 3. Data Transfer
                if "M" in buffer and ":" in buffer:
                    # מנקים רווחים שאולי נדבקו להתחלה
                    buffer = buffer.lstrip()

                    if buffer.startswith("M"):
                        parts = buffer.split(':', 1)
                        header = parts[0]
                        rest = parts[1]

                        if len(rest) >= max_msg_size:
                            seq_num = int(header[1:])

                            if seq_num == expected_seq:
                                conn.send(f"ACK{seq_num}".encode())
                                expected_seq += 1
                            else:
                                if expected_seq > 0:
                                    conn.send(f"ACK{expected_seq - 1}".encode())

                            buffer = buffer[len(header) + 1 + max_msg_size:]

        except Exception as e:
            print(f"Error: {e}")
        conn.close()


if __name__ == "__main__":
    start_server()
