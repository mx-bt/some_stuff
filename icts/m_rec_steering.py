import socket
from robomaster import robot
import time

# dh2   192.168.50.206
# ip    192.168.50.3

list_sn = ["3JKCK7W0030DCD","3JKCK7W0030CS5"] # javier stormtrooper

ep_robot = robot.Robot()
ep_robot.initialize(conn_type="sta", sn=list_sn[1])
ep_version = ep_robot.get_version()
ep_chassis = ep_robot.chassis
print(f"Robot Version {ep_version}")


# DANCE PROGRAM COLLETION
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

def baile_mexicano(_mode: int = 1, play_song = True):

        # ep_robot.play_audio(filename="trump_quote_mexico.wav").wait_for_completed()
        
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
                ep_robot.play_audio(filename="mexican_hat_dance.wav")
            else:
                time.sleep(1.75)
            
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

# ==============================



port = 12345
while True:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', port))
            s.listen()
            print(f"Waiting for incoming connections on port {port}...")
            conn, addr = s.accept()
            with conn:
                # print(f"Connected by {addr}")
                # data = conn.recv(1024).decode('utf-8').split() 
                message = str(conn.recv(1024).decode('utf-8'))

            print("Received dance order: ", message)
            if message == "Mexico":
                
                baile_mexicano(_mode = -1)

            
            # x_y_z_mt = tuple(round(float(num), 2) for num in data)

            # x_rec, y_rec, z_rec, mt_rec = x_y_z_mt[0], x_y_z_mt[1], x_y_z_mt[2], x_y_z_mt[3]
            # ep_robot.chassis.drive_speed(x=x_rec,
            #                                 y=y_rec,
            #                                 z=z_rec,
            #                                 timeout=5)
            # print(f"Executing dance move from {addr}: {x_rec, y_rec, z_rec, mt_rec}")
            # time.sleep(mt_rec)
            # ep_robot.chassis.drive_speed(x=0,y=0,z=0,timeout=5)

    except KeyboardInterrupt:
        ep_robot.close()
        break
