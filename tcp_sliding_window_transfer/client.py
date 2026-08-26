"""TCP sender for a configurable sliding-window file-transfer exercise."""

import socket
import time
import re
import os  # <--- חובה להוסיף את זה


def read_config(filename='config.txt'):
    config = {}
    # מציאת הנתיב המלא לקובץ כדי למנוע בעיות של "קובץ לא נמצא"
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, filename)

    try:
        with open(full_path, 'r') as file:
            for line in file:
                if ':' in line:
                    key, value = line.split(':', 1)
                    # === התיקון הקריטי למניעת הקריסה ===
                    # מנקה רווחים וגם מנקה גרשיים אם ישנם
                    config[key.strip()] = value.strip().strip('"').strip("'")
                    # ===================================
    except FileNotFoundError:
        print(f"[CLIENT] Config file not found at: {full_path}")
        print("Please enter values manually:")
        config['message'] = input("Enter file path to send (e.g., sample_payload.txt): ")
        config['timeout'] = input("Enter timeout in seconds (e.g., 3): ")
        config['window_size'] = input("Enter window_size (e.g., 5): ")
    return config


def start_client():
    # טעינת הגדרות
    config = read_config('config.txt')

    server_ip = '127.0.0.1'
    server_port = 12345

    # המרת הערכים לטיפוסים הנכונים
    window_size = int(config.get('window_size', 5))
    timeout_val = float(config.get('timeout', 2.0))
    file_path = config.get('message', 'sample_payload.txt')

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((server_ip, server_port))
        # הדפסה שתראה לך שהחיבור הצליח
        print(f"[CLIENT] Connected to server at {server_ip}:{server_port}")
    except ConnectionRefusedError:
        print("[CLIENT] Error: Could not connect to server. Is the server running?")
        return

    # Handshake & Setup
    print("[CLIENT] Starting handshake...")
    client_socket.send("SIN".encode())
    client_socket.recv(1024)
    client_socket.send("ACK\n".encode())
    time.sleep(0.5)
    print("[CLIENT] Handshake successful!")

    print("[CLIENT] Requesting Max Message Size...")
    client_socket.send("SIZE_REQ".encode())
    max_size = int(client_socket.recv(1024).decode())
    print(f"[CLIENT] Server agreed on max size: {max_size}")
    time.sleep(0.5)

    # קריאת הקובץ (שימוש בנתיב מלא גם כאן ליתר ביטחון)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_data_path = os.path.join(base_dir, file_path)

    try:
        with open(full_data_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"[ERROR] Data file not found at: {full_data_path}")
        return

    chunks = [content[i:i + max_size] for i in range(0, len(content), max_size)]
    total = len(chunks)
    base = 0
    next_seq = 0

    print(f"[CLIENT] Starting transmission. Total chunks: {total}, Window: {window_size}")

    # הלולאה הראשית (Sliding Window)
    while base < total:
        # שליחת הודעות בחלון
        while next_seq < base + window_size and next_seq < total:
            msg = f"M{next_seq}:{chunks[next_seq]}"
            client_socket.send(msg.encode())
            # print(f"[CLIENT] Sent packet M{next_seq}") # אופציונלי לדיבוג
            next_seq += 1
            time.sleep(0.1)

        # קבלת אישורים
        try:
            client_socket.settimeout(timeout_val)
            ack = client_socket.recv(1024).decode()
            if "ACK" in ack:
                nums = re.findall(r'ACK(\d+)', ack)
                for n in nums:
                    val = int(n)
                    if val >= base:
                        base = val + 1
        except socket.timeout:
            print(f"[DEBUG] Timeout! Base: {base}, Waiting for ACKs...")
            next_seq = base

    # הדפסת סיום - זה מה שאתה רוצה לראות בסוף
    print("[CLIENT] File transfer completed successfully.")
    client_socket.close()


if __name__ == "__main__":
    start_client()
