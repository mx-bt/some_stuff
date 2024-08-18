import socket

# dh2   192.168.50.206
# ip    192.168.50.3

def send_message(dest_ip, dest_port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((dest_ip, dest_port))
        s.sendall(message.encode('utf-8'))

if __name__ == "__main__":
    # IP-Adresse und Port des Empfängers
    receiver_ip = "192.168.50.206" # Max Privat
    receiver_port = 12345  # Wähle einen freien Port

    while True:
        try:
            # Nachricht, die gesendet werden soll
            message_to_send = input("Nachricht: ")

            # Sende die Nachricht
            send_message(receiver_ip, receiver_port, message_to_send)
        except KeyboardInterrupt:
            break