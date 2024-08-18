import socket
from robomaster import robot, led

# initialization: same program for Client and Server (set up Server first)

s = int(input("Enter 0 for Client (Master), 1 or 2 for Server (Slave): "))
list_robot_serial_numbers = ["3JKCK7W0030DCD",  "3JKCK7W0030CS5", "3JKCK7W0030DFA"] # Javier, Stormtrooper, NoName
list_laptop_ips = ["192.168.50.206", "192.168.50.43","192.168.50.3",]  # max priv, marco, max arbeit


ep_robot = robot.Robot()
ep_robot.initialize(conn_type="sta", sn=list_robot_serial_numbers[s]) # NoName oder Stormtrooper
print(ep_robot.get_version())
ep_led = ep_robot.led

# Protokoll
#
# die einzelnen Schritte (Funktionen) haben Codes (A1-A9)
#
# Output einer Funktion ist eine Variable (r), die gesendet wird,
# die nächste Funktion aufruft und gleichzeitig deren Input ist
#
# Gerade Funktion:   Slave  führt aus
# Ungerade Funktion: Master führt aus
# AX-0:		         negativer Output
# AX-1:		         positiver Output


def A1(r):
    print(f"{r} running")
    ep_robot.play_audio(filename="protocol_audios\A1.wav").wait_for_completed()
    try:
        r = "A2-1-" + ep_robot.get_sn()
    except:
        r = "A2-0"
    client_socket.send(r.encode())
    print(f"function finished")


def A2(r):
    print(f"{r} running")
    ep_robot.play_audio(filename="protocol_audios\A2.wav").wait_for_completed()
    if r == "A2-0":
        print(f"The connected Computer is not connected to a Robot, Connecton will be closed...")
        r = "A3-0"
        client_socket.send(r.encode())
    else:
        sn = r[5:]  # store serial number in separate variable
        print(f"Robot with Serial number {sn} connected!")
        r = "A3-1"
        client_socket.send(r.encode())
    print(f"function finished")


def A3(r):
    print(f"{r} running")
    ep_robot.play_audio(filename="protocol_audios\A3.wav").wait_for_completed()
    if r == "A3-0":
        print(f"The Connection has been closed by the Server.")
        r = "AX"
    else:
        input(f"Press Enter key to ask the other robot to dance")
        r = "A4"
    client_socket.send(r.encode())
    print(f"function finished")


def A4(r):
    print(f"{r} running")
    print(f"Question recieved: May I dance with the other robot?")
    ep_robot.play_audio(filename="protocol_audios\A4.wav").wait_for_completed()
    i = ""
    while i != "yes" and i != "no":
        i = input("Please answer with yes / no:  ")
        if i == "yes":
            print(f"Nice, let's start")
            ep_robot.play_audio(filename="protocol_audios\A4-1.wav").wait_for_completed()
            ep_led.set_led(comp=led.COMP_ALL, r=250, g=0, b=0, effect=led.EFFECT_ON)
            r = "A5-1"
        elif i == "no":
            print(f"Lucky me, I can't even dance...")
            ep_robot.play_audio(filename="protocol_audios\A4-0.wav").wait_for_completed()
            r = "A5-0"
        else:
            print("Try again")
    client_socket.send(r.encode())
    print(f"function finished")


def A5(r):
    print(f"{r} running")
    if r == "A5-0":
        ep_robot.play_audio(filename="protocol_audios\A5-0.wav").wait_for_completed()
        print(f"Negative Response :(, closing the connection")
        r = "AX"
    else:
        ep_robot.play_audio(filename="protocol_audios\A5-1.wav").wait_for_completed()
        ep_led.set_led(comp=led.COMP_ALL, r=250, g=0, b=0, effect=led.EFFECT_ON)
        print(f"Positive Response :), starting the dance program!")
        r = "A6"
    client_socket.send(r.encode())
    print(f"function finished")

def A6(r):
    print(f"{r} running")
    print(f"I am READY")
    r = "A7"
    client_socket.send(r.encode())
    ep_robot.play_audio(filename="protocol_audios\countdown.wav").wait_for_completed()
    print(f"function finished")


def A7(r):
    print(f"{r} running")
    ep_robot.play_audio(filename="protocol_audios\countdown.wav").wait_for_completed()
    print(f"Other Roboter has confirmed: READY to dance")
    print(f"Starting the dance program")
    ep_robot.play_audio(filename="protocol_audios\music.wav").wait_for_completed()
    print(f"The dance is over...")
    ep_led.set_led(comp=led.COMP_ALL, r=80, g=0, b=80, effect=led.EFFECT_ON)
    ep_robot.play_audio(filename="protocol_audios\A7-End.wav").wait_for_completed()
    r = "A8"
    client_socket.send(r.encode())
    print(f"function finished")


def A8(r):
    print(f"{r} running")
    print(f"The dance is over..., closing the connection")
    ep_led.set_led(comp=led.COMP_ALL, r=80, g=0, b=80, effect=led.EFFECT_ON)
    ep_robot.play_audio(filename="A8.wav").wait_for_completed()
    r = "A9"
    client_socket.send(r.encode())
    print(f"function finished")


def A9(r):
    print(f"{r} running")
    print("Closing the connection")
    r = "AX"
    client_socket.send(r.encode())
    print(f"function finished")





# set up Client if 0, set up Server if 1

if s == 0:
    # Master - Start

    ep_led.set_led(comp=led.COMP_ALL, r=0, g=0, b=255, effect=led.EFFECT_ON)

    # Client - Start

    host = list_laptop_ips[2] # '127.0.0.1'  # IP-Address ('127.0.0.1' for local test)
    port = 12345  # Port

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create Socket
    client_socket.connect((host, port))
    print(f"Connecting with Robot, IP {host}")

else:
    # Slave(s) - Start

    ep_led.set_led(comp=led.COMP_ALL, r=255, g=0, b=0, effect=led.EFFECT_ON)
    
    # Server - Start
    host = list_laptop_ips[0]  # IP-Address ('127.0.0.1' for local test)
    port = 12345  # Port

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create Socket
    server_socket.bind((host, port))
    server_socket.listen(1)

    print(f"Computer is ready to connect")
    client_socket, client_address = server_socket.accept()
    print(f"Incoming connection, IP {client_address}")

    r = "A1"  # Send Command to run Function A1 on other Computer
    client_socket.send(r.encode())


# While-Loop to keep listening for incoming messages if no function is running

while True:
    r = client_socket.recv(1024).decode()
    print(f"--------------------------------------")
    print(f"Recieved message {r}")
    function_code = r[:2]  # variable = function code (first two letters of message "r"), to start new function

    if r == "AX":  # function code / message = "AX" = end program, also send order to other computer
        print("closing connection...")
        client_socket.send(r.encode())
        client_socket.close()
        break

    if function_code in globals() and callable(globals()[function_code]):  # call function with the function code
        print(f"Calling function {function_code} with Input {r}")
        globals()[function_code](r)
    else:  # or break from loop if program if code not found
        print(f"Function {function_code} / {r} not found.")
        break