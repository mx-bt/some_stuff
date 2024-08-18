import socket
from robomaster import robot

    # Protokoll
    #
    # die einzelnen Schritte (Funktionen) haben Codes (A1-A9)
    #
    # Output einer Funktion ist eine Variable (r), die gesendet wird,
    # die nächste Funktion aufruft und gleichzeitig deren Input ist
    #
    # Gerade Funktion:   Server führt aus
    # Ungerade Funktion: Client führt aus
    # AX-0:		         negativer Output
    # AX-1:		         positiver Output



def A1(r):
    print(f"{r} running")
    try:
        r = "A2-1: " & robot.get_sn
    except:
        r = "A2-0"
    client_socket.send(r.encode())
    print(f"function finished")


def A2(r):
    print(f"{r} running")
    if r == "A2-0":
        print(f"The connected Computer is not connected to a Robot, Connecton will be closed...")
        r = "A3-0"
        client_socket.send(r.encode())
        #client_socket.close()
    else:
        sn = r      #Seriennummer in separater Variable speichern (für späteren Zugriff)
        print(f"Robot with Serial number {sn} connected!")
        r = "A3-1"
        client_socket.send(r.encode())
    print(f"function finished")


def A3(r):
    print(f"{r} running")
    if r == "A3-0":
        print(f"The Connection has been closed by the Server.")
        client_socket.close()
    else:
        print(f"The Connection has been established, now asking for a dance")
        r = "A4"
        client_socket.send(r.encode())
    print(f"function finished")


def A4(r):
    print(f"{r} running")
    print(f"Question recieved: May I dance with the other robot?")
    r = input("Please answer with yes / no:  ")
    if r == "yes":
        print(f"Nice, let's start")
        r = "A5-1"
    elif r == "no":
        print(f"Lucky me, I can't even dance...")
        r = "A5-0"
    else:
        print(f"Try Again, input yes or no")
        A4(r)
    client_socket.send(r.encode())
    print(f"function finished")


def A5(r):
    print(f"{r} running")
    if r == "A5-0":
        print(f"Negative Response :(, closing the connection")
        client_socket.close()
    else:
        print(f"Positive Response :), starting the dance program!")
        r = "A6"
        client_socket.send(r.encode())
        ### robot.play_audio(filename="demo1.wav").wait_for_completed()
    print(f"function finished")


def A6(r):
    print(f"{r} running")
    ### robot.play_audio(filename="demo1.wav").wait_for_completed()
    print(f"I am READY")
    r = "A7"
    client_socket.send(r.encode())
    print(f"function finished")


def A7(r):
    print(f"{r} running")
    print(f"Other Roboter has confirmed: READY to dance")
    print(f"Starting the dance program")
    #dance()
    print(f"The dance is over...")
    r = "A8"
    client_socket.send(r.encode())
    print(f"function finished")


def A8(r):
    print(f"{r} running")
    print(f"The dance is over..., closing the connection")
    r = "A9"
    client_socket.send(r.encode())
    client_socket.close()
    print(f"function finished")


def A9(r):
    print(f"{r} running")
    print("Closing the connection")
    client_socket.close()
    print(f"function finished")


s = input("Bitte 0 für Client, 1 für Server eingeben: ")


if s == "0":
    # Client - Start8
    # 192.168.50.206 (Max Privat)
    host = '192.168.50.206'  # IP-Address ('127.0.0.1' for local test)
    port = 12345        # Port

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create Socket
    client_socket.connect((host, port))
    print(f"Connecting with Robot, IP {host}")

else:
    # Server - Start 
    # 192.168.50.3 (Max Arbeit)
    host = '192.168.50.3'  # IP-Address ('127.0.0.1' for local test)
    port = 12345        # Port

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create Socket
    server_socket.bind((host, port))
    server_socket.listen(1)

    print(f"Computer is ready to connect")
    client_socket, client_address = server_socket.accept()
    print(f"Incoming connection, IP {client_address}")

    r = "A1"                                    # Send Command to run A1 on other Computer
    client_socket.send(r.encode())


while True:
    r = client_socket.recv(1024).decode()
    print(f"--------------------------------------")
    print(f"Recieved message {r}")
    variable = r[:2]
    if variable in globals() and callable(globals()[variable]):
        print(f"Calling function {variable} with Input {r}")
        globals()[variable](r)
    else:
        print(f"Function {variable} / {r} not found.")
        break