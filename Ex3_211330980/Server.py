import socket
import random

def read_config(filename):
    config = {}
    try:
        with open(filename, 'r') as file:
            for line in file:
                if ':' in line:
                    key, value = line.split(':', 1)
                    config[key.strip()] = value.strip()
    except FileNotFoundError:
        # כאן הוספנו את התמיכה בקלט ידני במקרה שהקובץ לא נמצא
        # זה לא סותר את צילום המסך כי זה קורה בתוך ה-except
        print(f"[SERVER] Config file '{filename}' not found. Please enter values manually:")
        config['maximum_msg_size'] = input("Enter maximum_msg_size (e.g., 100): ")
        config['window_size'] = input("Enter window_size (e.g., 5): ")
        config['dynamic message size'] = input("Enable dynamic message size? (True/False): ")
        config['drop_prob'] = input("Enter packet drop probability (0.0 - 1.0): ")
    return config

def start_server():
    config = read_config('input.txt')
    # שימוש בערכים מהקונפיגורציה (עם ברירות מחדל למקרה של בעיה)
    max_msg_size = int(config.get('maximum_msg_size', '100'))
    drop_prob = float(config.get('drop_prob', '0.0'))

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('127.0.0.1', 12345))
    server_socket.listen(1)

    print(f"[SERVER] Listening... (Drop Rate: {drop_prob})")

    while True:
        conn, addr = server_socket.accept()
        expected_seq = 0
        buffer = ""

        try:
            while True:
                data = conn.recv(1024).decode()
                if not data: break
                buffer += data

                # Handshake & Cleanup
                if "SIN" in buffer:
                    conn.send("SIN/ACK".encode())
                    buffer = buffer.replace("SIN", "")
                if "ACK" in buffer and "M" not in buffer:
                    buffer = buffer.replace("ACK", "").replace("\n", "").strip()
                if "SIZE_REQ" in buffer:
                    conn.send(str(max_msg_size).encode())
                    buffer = buffer.replace("SIZE_REQ", "")

                # Data Transfer Logic
                if "M" in buffer and ":" in buffer:
                    buffer = buffer.lstrip()
                    if buffer.startswith("M"):
                        parts = buffer.split(':', 1)
                        header = parts[0]
                        rest = parts[1]

                        if len(rest) >= max_msg_size:
                            # סימולציה של איבוד חבילה
                            if random.random() < drop_prob:
                                print(f"[SERVER] DROPPED packet {header} intentionally!")
                                # מוחקים מהבאפר (כאילו התקבל) אבל לא שולחים ACK
                                buffer = buffer[len(header) + 1 + max_msg_size:]
                                continue

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