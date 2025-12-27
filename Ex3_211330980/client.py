import socket
import time


def start_client():
    server_ip = '127.0.0.1'
    server_port = 12345
    window_size = 5

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

    # קריאת הקובץ
    with open('my_data.txt', 'r') as f:
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
            time.sleep(0.1)  # השהיה למניעת הדבקה

        # קבלת אישורים
        try:
            client_socket.settimeout(2.0)
            ack = client_socket.recv(1024).decode()
            if "ACK" in ack:
                import re
                nums = re.findall(r'ACK(\d+)', ack)
                for n in nums:
                    val = int(n)
                    if val >= base:
                        base = val + 1
        except socket.timeout:
            next_seq = base

    client_socket.close()


if __name__ == "__main__":
    start_client()