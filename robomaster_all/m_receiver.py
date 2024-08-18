import socket
import robomaster

# dh2   192.168.50.206
# ip    192.168.50.3

def receive_messages(port):
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                s.listen()
                print(f"Waiting for incoming connections on port {port}...")
                conn, addr = s.accept()
                with conn:
                    # print(f"Connected by {addr}")
                    data = conn.recv(1024)
                    print(f"Message from {addr}: {data.decode('utf-8')}")
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    # Port, auf dem der Empfänger auf eingehende Nachrichten wartet
    receiver_port = 12345  # Wähle denselben Port wie im Sender

    # Starte den Thread für den Empfänger, um auf eingehende Nachrichten zu warten
    receive_messages(receiver_port)