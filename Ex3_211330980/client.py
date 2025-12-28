import socket
import time
import re


# הוספנו פונקציית קריאה גם ללקוח כדי לעמוד בדרישות
def read_config(filename):
    config = {}
    try:
        with open(filename, 'r') as file:
            for line in file:
                if ':' in line:
                    key, value = line.split(':', 1)
                    config[key.strip()] = value.strip()
    except FileNotFoundError:
        print(f"[CLIENT] Config file '{filename}' not found. Please enter values manually:")
        config['message'] = input("Enter file path to send (e.g., my_data.txt): ")
        config['timeout'] = input("Enter timeout in seconds (e.g., 3): ")
        config['window_size'] = input("Enter window_size (e.g., 5): ")
    return config


def start_client():
    # טעינת הגדרות
    config = read_config('input.txt')

    server_ip = '127.0.0.1'
    server_port = 12345

    # קריאת הפרמטרים מהקובץ (או ברירת מחדל אם חסר)
    window_size = int(config.get('window_size', 5))
    timeout_val = float(config.get('timeout', 2.0))
    file_path = config.get('message', 'my_data.txt')

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))

    # Handshake & Setup
    client_socket.send("SIN".encode())
    client_socket.recv(1024)
    client_socket.send("ACK\n".encode())
    time.sleep(0.5)

    client_socket.send("SIZE_REQ".encode())
    max_size = int(client_socket.recv(1024).decode())
    time.sleep(0.5)

    # קריאת הקובץ (משתמש בנתיב מהקונפיגורציה)
    with open(file_path, 'r') as f:
        content = f.read()

    chunks = [content[i:i + max_size] for i in range(0, len(content), max_size)]
    total = len(chunks)
    base = 0
    next_seq = 0

    # הלולאה הראשית
    while base < total:
        # שליחת הודעות בחלון
        while next_seq < base + window_size and next_seq < total:
            msg = f"M{next_seq}:{chunks[next_seq]}"
            client_socket.send(msg.encode())
            next_seq += 1
            time.sleep(0.1)

        # קבלת אישורים
        try:
            client_socket.settimeout(timeout_val)  # שימוש בערך מהקובץ
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

    client_socket.close()


if __name__ == "__main__":
    start_client()