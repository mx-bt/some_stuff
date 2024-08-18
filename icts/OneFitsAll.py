# Configuration for setup
_robot_no = 2 # 0 = Master, 1 = right, 2 = left
_connection_type = "sta" # "ap" oder "sta"

list_robot_serial_numbers = ["3JKCK7W0030DCD",  "3JKCK7W0030CS5", "3JKCK7W0030DFA"] # Javier, Stormtrooper, NoName
list_laptop_ips = ["192.168.50.206","192.168.50.3", "192.168.50.43",] # max priv, marco, max arbeit,

"""
STRUKTUR GESAMTPROGRAMM GP

I   Initialisierung und Coupling (✔)
II  Tanzprogramm (X)
III Auflösung und Neu-Initialisierung

I
1. Aufteilung der Roboter + Zuweisung der Rollen (✔)
2. Initialisierung und Ausrichtung der Roboters (✔)
3. Zufällige Auswahl Zielroboter für Tanzanfrage (✔)
4. Informationsaustausch und Coupling (X)

II
1. Fahrt zum Zentrum der Tanzfläche (✔)
2. Durchführung Tanzprogramm (✔)

III
1. Kalibrierung? (X)

===
Grobe Struktur der Partnersuche + Auflösung
RoboterDanceOperatingSystem Pseudocode
default: [State] {Roboter suchen}
	wenn gefunden: [State] Roboter [0] Fragen ob Tanz
		wenn positiv [State] Tanzen mit Roboter [0]
			wenn Tanzen abgeschlossen [State] {Roboter [1] suchen}
		wenn negativ [State] {Roboter [1] suchen}

Roboter haben fixe Position auf der Map, zu denen Sie nach jeder Interaktion zurückkehren.

Nach  (via IP des PCs, Abfrage: input("Tanzen Y/N: ")
	wenn positivem Handshake
		beide Roboter fahren zur Mitte
		Tanzprogramm wird ausgeführt (Vorprogrammiert oder Individuell)
		Roboter richten sich N-S aus
		Robter kehren zurück

"""
from robomaster import robot, led
import time
import random
import socket
from datetime import datetime

ep_robot = robot.Robot()
ep_robot.initialize(conn_type=_connection_type, sn=list_robot_serial_numbers[_robot_no])

_robot_version = ep_robot.get_version()
print(f"Roboter {_robot_no} verbunden. Robot Version {_robot_version}")

ep_chassis = ep_robot.chassis
ep_led = ep_robot.led
    
# Define core functions and dance programs

def send_message_v2(message: str, destination_ip, destination_port):
    """will only initiate dance programs between robots"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((destination_ip, destination_port))
            s.sendall(message.encode('utf-8'))
        timestamp = datetime.now().timestamp()
        date_time = datetime.fromtimestamp(timestamp)
        print(f"Message: {message} [{date_time}]")
    except Exception:
        pass

def custom_move(x_or_y, movetime, val):
    if x_or_y == "x":
        # send_message_v1(f"{val} 0 0 {movetime}")
        ep_chassis.drive_speed(x=val, timeout=5)
        time.sleep(movetime)
        ep_chassis.drive_speed(x=0, y=0, z=0, timeout=5)

    elif x_or_y == "y":
        # send_message_v1(f"0 {val} 0 {movetime}")
        ep_chassis.drive_speed(y=val, timeout=5)
        time.sleep(movetime)
        ep_chassis.drive_speed(x=0, y=0, z=0, timeout=5)

    elif x_or_y == "n":
        # send_message_v1(f"0 0 0 {movetime}")
        ep_chassis.drive_speed(x=0, y=0, z=0, timeout=5)
        time.sleep(movetime)

    else:
        print("Error in custom_move function")

def whisper_dance(_mode: int = 1, play_song = True):
    xy_speed_value, z_speed_val  = 0.25, 15
    move_timez = 1 # seconds
    
    if play_song:
        print("plays song")
        ep_robot.play_audio(filename="careless_whispers.wav") # 14 Sekunden
    else:
        print("waits a moment")
        time.sleep(1.75)
    if _mode == 2:
        if (_robot_no==0) or (_robot_no==1):

            ep_chassis.move(z = -30, z_speed = z_speed_val).wait_for_completed()
            ep_chassis.move(x = 0.3, xy_speed = xy_speed_value).wait_for_completed()

            ep_chassis.drive_speed(x=0, y=0, z=z_speed_val, timeout=5)
            time.sleep(0.5)
            ep_chassis.drive_speed(x=0, y=0, z=-z_speed_val, timeout=5)
            time.sleep(1)
            ep_chassis.drive_speed(x=0, y=0, z=z_speed_val, timeout=5)
            time.sleep(0.5)

            ep_chassis.move(x = -0.3, xy_speed = xy_speed_value).wait_for_completed()
            ep_chassis.move(z = 180, z_speed = z_speed_val).wait_for_completed()
            ep_chassis.move(x = -0.3, xy_speed = xy_speed_value).wait_for_completed()

            ep_chassis.drive_speed(x=0, y=0, z=z_speed_val, timeout=5)
            time.sleep(0.5)
            ep_chassis.drive_speed(x=0, y=0, z=-z_speed_val, timeout=5)
            time.sleep(1)
            ep_chassis.drive_speed(x=0, y=0, z=z_speed_val, timeout=5)
            time.sleep(0.5)

            # erstmal Zeit checken 
        else:
            pass

def baile_mexicano(_mode: int = 1, play_song = True):

    xy_speed_value, z_speed_val  = 0.5, 30
    move_timez = 0.5 # seconds

    def movimiento_del_culo(movetime):
        for _ in range(2):

            # send_message_v1(f"0 0 {z_val} {movetime}")
            ep_chassis.drive_speed(x=0, y=0, z=z_speed_val*_mode, timeout=5)
            time.sleep(movetime)
            
            # send_message_v1(f"0 0 {-z_val} {movetime}")
            ep_chassis.drive_speed(x=0, y=0, z=-z_speed_val*_mode, timeout=5)
            time.sleep(movetime)

            ep_chassis.drive_speed(x=0, y=0, z=0, timeout=5)
            time.sleep(0)

    # direction = (-1)**n
    for c in range(2):
        if play_song:
            print("plays song")
            ep_robot.play_audio(filename="mexican_hat_dance.wav")
        else:
            print("waits a moment")
            time.sleep(2) # evtl. Verzögerung überbrücken + sicherstellen, dass Slave dem Master folgt

        for n in range(2):
            # ep_robot.play_audio(filename="mexican_hat_dance.wav")
            custom_move("x",move_timez,xy_speed_value*((-1)**n)*_mode)
            custom_move("y",move_timez,xy_speed_value*((-1)**(n+c))*_mode)
            movimiento_del_culo(move_timez)
            custom_move("x",move_timez,xy_speed_value*((-1)**(n+1))*_mode)
            custom_move("y",move_timez,xy_speed_value*((-1)**(n+1+c))*_mode)
            movimiento_del_culo(move_timez)
            custom_move("n",0,0)
            time.sleep(1)

# ===

def init_cold_approach(try_target = 1):
    # drive to middle
        # try_target = 2 # random.choice([1, 2])
    print(f"Master just chose Robot {try_target} to approach")
    if try_target == 1:
        ep_chassis.move(z=-45, z_speed=z_speed).wait_for_completed()
        ep_chassis.move(x=0.8, xy_speed=xy_speed).wait_for_completed()
        ep_chassis.move(x=0,y=0,z=0).wait_for_completed()
        # Conversation

    elif try_target == 2:
        ep_chassis.move(z=45, z_speed=z_speed).wait_for_completed()
        ep_chassis.move(x=0.8, xy_speed=xy_speed).wait_for_completed()
        ep_chassis.move(x=0,y=0,z=0).wait_for_completed()
        # Conversation
    else:
        pass

def recenter_after_cold_approach(tried_target = 1):
    print(f"Master comes back from Robot {tried_target}")
    if tried_target == 1:
        # Conversation
        ep_chassis.move(x=-0.8, xy_speed=xy_speed).wait_for_completed()
        ep_chassis.move(z=45, z_speed=z_speed).wait_for_completed()
        ep_chassis.move(x=0,y=0,z=0).wait_for_completed()

    elif tried_target == 2:
        # Conversation
        ep_chassis.move(x=-0.8, xy_speed=xy_speed).wait_for_completed()
        ep_chassis.move(z=-45, z_speed=z_speed).wait_for_completed()
        ep_chassis.move(x=0,y=0,z=0).wait_for_completed()
    else:
        pass


# Initialisierung Roboterpositionen (wie auf Bild)
# 390x245x330mm pro Roboter = 0.39x0.245x0.33m (LxBxH)

xy_speed = 1
z_speed = 90

if _robot_no == 0:
    ep_led.set_led(comp=led.COMP_ALL, r=0, g=0, b=255, effect=led.EFFECT_ON) # Blau
    time.sleep(0) # hoch setzen!
    ep_chassis.move(x=1.5, xy_speed=xy_speed).wait_for_completed()

    # Nachricht an Slave wenn zurück
else:
    if _robot_no == 1:
        # start pos roboter 1 daher 0.3m nach rechts verschoben [ANPASSEN]
        ep_led.set_led(comp=led.COMP_ALL, r=255, g=0, b=0, effect=led.EFFECT_ON) # rot
        ep_chassis.move(x=3, y=1.2, z=0, xy_speed=xy_speed).wait_for_completed()
        ep_chassis.move(z=180, z_speed=z_speed).wait_for_completed()
    elif _robot_no == 2:
        # start pos roboter 2 daher 0.3m nach links verschoben [ANPASSEN]
        ep_led.set_led(comp=led.COMP_ALL, r=255, g=0, b=0, effect=led.EFFECT_ON) # rot
        ep_chassis.move(x=3, y=-1.2, z=0, xy_speed=xy_speed).wait_for_completed()
        ep_chassis.move(z=180, z_speed=z_speed).wait_for_completed()
    else:
        print("Fehler bei der Roboterinitialisierung")

# Master sucht sich zufällig einen gewünschten Tanzpartner aus
#
""" HIER PROGRAMM ZUM ELEKTRONISCHEN HANDSHAKE/AUSWAHL EINFÜGEN (ERSTE KOMMUNIKATION BEGINNT)""" 
#


if _robot_no == 0:
    target = random.choice([1, 2])
    init_cold_approach(try_target=target)
    # conversation protocol
    time.sleep(0.5)
    recenter_after_cold_approach(tried_target=target)
    # 
    if target == 1:
        target = 2
    else:
        target = 1
    #
    init_cold_approach(try_target=target)
    # conversation protocol
    time.sleep(0.5)
    recenter_after_cold_approach(tried_target=target)
else:
    pass
#

def protocol_L():
    return [0,0,1]
outcome_cold_approach = protocol_L()

"""PROGRAMM ZUM TANZEN"""
if _robot_no == 0:
    # Übernimmt Senderrolle, Wählt Tanzprogramm
    # Copy+Pase von m_sen_steering.py

    for robo_nr in range(1,3):
        if outcome_cold_approach[robo_nr] == 1:
            print("Recenter command...")
            send_message_v2("Come_to_daddy", list_laptop_ips[robo_nr], 12345 )

    time.sleep(5)
    dances = ["Mexico","Whisper"]
    choice_of_dance = 0 # random.choice([0,1])

    for robo_nr in range(1,3):
        if outcome_cold_approach[robo_nr] == 1:
            print("Dance command...")
            send_message_v2(str(dances[choice_of_dance]), list_laptop_ips[robo_nr], 12345)
    timestamp = datetime.now().timestamp()
    date_time = datetime.fromtimestamp(timestamp)
    print(f"dance starts now [{date_time}]")
    baile_mexicano(_mode = 1, play_song= True)

    print("try_whisper")

    time.sleep(3)
    for robo_nr in range(1,3):
        if outcome_cold_approach[robo_nr] == 1:
            print("Dance command...")
            send_message_v2("Whisper", list_laptop_ips[robo_nr], 12345)
    whisper_dance(_mode = 2, play_song=True)

    # Aktuell hier Ende ===
    


elif (_robot_no == 1) or (_robot_no == 2):
      
    # Warten auf Tanzwahl 
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', 12345))
                s.listen()
                # print(f"Waiting for incoming connections on port {port}...")
                conn, addr = s.accept()
                with conn:
                    # print(f"Connected by {addr}")
                    # data = conn.recv(1024).decode('utf-8').split()
                    order = str(conn.recv(1024).decode('utf-8'))
                # xyz = tuple(round(float(num), 2) for num in data)
                # print(f"Command from {addr}: {xyz}")
                timestamp = datetime.now().timestamp()
                date_time = datetime.fromtimestamp(timestamp)
                print(f"Message rec: {order} [{date_time}]")
                # ep_robot.chassis.drive_speed(x=-xyz[0],y=xyz[1]*0.5,z=xyz[2]*100,timeout=0)

                if order == "Come_to_daddy":
                        # Falls Roboter zugesagt hat, folgt er dem Master auf den Dancefloor
                    if _robot_no == 1:
                        ep_chassis.move(z=-45, z_speed=z_speed).wait_for_completed()
                        ep_chassis.move(x=1, xy_speed=xy_speed).wait_for_completed()
                        ep_chassis.move(z=45, z_speed=z_speed).wait_for_completed()
                        ep_chassis.move(x=0,y=0,z=0).wait_for_completed()
                    else:
                        pass
                    if _robot_no == 2:
                        ep_chassis.move(z=45, z_speed=z_speed).wait_for_completed()
                        ep_chassis.move(x=1, xy_speed=xy_speed).wait_for_completed()
                        ep_chassis.move(z=-45, z_speed=z_speed).wait_for_completed()
                        ep_chassis.move(x=0,y=0,z=0).wait_for_completed()
                    else:
                        pass
                    
                elif order == "Mexico":
                    baile_mexicano(_mode = -1, play_song= False)

                elif order == "Whisper":
                    whisper_dance(_mode = 2, play_song = False)

                # answer replacement solution for communication program
                elif order == "wanna_dance":
                    answer = ["yes","no"][random.choice([0,1])]
                    send_message_v2("Whisper", list_laptop_ips[0], 12345)
            
                else:
                    print("Command not possible")

        except KeyboardInterrupt:
            ep_robot.close()
            break
    
    pass
else:
    pass