import socket
import random
import os


def read_config(filename='input.txt'):
    config = {}
    # מציאת הנתיב המלא
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, filename)

    try:
        with open(full_path, 'r') as file:
            for line in file:
                if ':' in line:
                    key, value = line.split(':', 1)
                    # === התיקון נמצא כאן ===
                    # מנקה רווחים ואז מנקה גרשיים אם יש
                    config[key.strip()] = value.strip().strip('"').strip("'")
                    # =======================
    except FileNotFoundError:
        print(f"[CLIENT] Config file not found at: {full_path}")
        print("Please enter values manually:")
        config['message'] = input("Enter file path to send (e.g., my_data.txt): ")
        config['timeout'] = input("Enter timeout in seconds (e.g., 3): ")
        config['window_size'] = input("Enter window_size (e.g., 5): ")
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