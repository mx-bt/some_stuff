import socket
import pygame
import time
from robomaster import robot
# dh2   192.168.50.206
# ip    192.168.50.3
ep_robot = robot.Robot()
destination_ip = "192.168.50.3" # Max Arbeit
destination_port = 12345  # Wähle einen freien Port

list_robot_serial_numbers = ["3JKCK7W0030DCD", "3JKCK7W0030CS5", "3JKCK7W0030DFA"] # Javier, , Stormtrooper, NoName

try:
    ep_robot.initialize(conn_type="sta", sn=list_robot_serial_numbers[0]) # config sn
except Exception as e:
    time.sleep(1)
print(f"Robot Version {ep_robot.get_version()}")

ep_chassis = ep_robot.chassis



# def send_message_v2(message: str):
#     """will only initiate dance programs between robots"""
#     try:
#         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#             s.connect((destination_ip, destination_port))
#             s.sendall(message.encode('utf-8'))
#             print(f"Dance order: {message}")
#     except Exception:
#         pass

# def custom_move(x_or_y, movetime, val):
#     if x_or_y == "x":
#         # send_message_v1(f"{val} 0 0 {movetime}")
#         ep_chassis.drive_speed(x=val, timeout=5)
#         time.sleep(movetime)
#         ep_chassis.drive_speed(x=0, y=0, z=0, timeout=5)

#     elif x_or_y == "y":
#         # send_message_v1(f"0 {val} 0 {movetime}")
#         ep_chassis.drive_speed(y=val, timeout=5)
#         time.sleep(movetime)
#         ep_chassis.drive_speed(x=0, y=0, z=0, timeout=5)

#     elif x_or_y == "n":
#         # send_message_v1(f"0 0 0 {movetime}")
#         ep_chassis.drive_speed(x=0, y=0, z=0, timeout=5)
#         time.sleep(movetime)

#     else:
#         print("Error in custom_move function")

# def baile_mexicano(_mode: int = 1):

#         # ep_robot.play_audio(filename="trump_quote_mexico.wav").wait_for_completed()
        
#         xy_speed_value, z_speed_val  = 0.5, 30
#         move_timez = 0.5 # seconds

#         def movimiento_del_culo(movetime):
#             for _ in range(2):

#                 # send_message_v1(f"0 0 {z_val} {movetime}")
#                 ep_chassis.drive_speed(x=0, y=0, z=z_speed_val*_mode, timeout=5)
#                 time.sleep(movetime)
                
#                 # send_message_v1(f"0 0 {-z_val} {movetime}")
#                 ep_chassis.drive_speed(x=0, y=0, z=-z_speed_val*_mode, timeout=5)
#                 time.sleep(movetime)

#                 ep_chassis.drive_speed(x=0, y=0, z=0, timeout=5)
#                 time.sleep(0)

                
#         # direction = (-1)**n
        
#         for c in range(2):
            
#             ep_robot.play_audio(filename="mexican_hat_dance.wav")

            
#             for n in range(2):

#                 # ep_robot.play_audio(filename="mexican_hat_dance.wav")
                
#                 custom_move("x",move_timez,xy_speed_value*((-1)**n)*_mode)
                
#                 custom_move("y",move_timez,xy_speed_value*((-1)**(n+c))*_mode)
                
#                 movimiento_del_culo(move_timez)
                
#                 custom_move("x",move_timez,xy_speed_value*((-1)**(n+1))*_mode)
                
#                 custom_move("y",move_timez,xy_speed_value*((-1)**(n+1+c))*_mode)
                
#                 movimiento_del_culo(move_timez)

#                 custom_move("n",0,0)

#                 time.sleep(1)

def send_message_v1(message: str):
    """x y z"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((destination_ip, destination_port))
            s.sendall(message.encode('utf-8'))
            print(f"Dance move to ({destination_ip}): ", message)
    except Exception:
        pass


if __name__ == "__main__":

    # Initialisiere den Joystick
    pygame.init()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    # send_message_v2("Mexico")
    # baile_mexicano(_mode = 1)
    try:
        ep_robot.play_audio(filename="titanic_flute.wav")
        while True:
            for event in pygame.event.get():
                if event.type == pygame.JOYAXISMOTION:
                    pygame.event.pump()

                    axis_x = joystick.get_axis(1)
                    axis_y = joystick.get_axis(0)
                    axis_z = joystick.get_axis(3)
                    ep_robot.chassis.drive_speed(x=-axis_x,y=axis_y*0.5,z=axis_z*100,timeout=0)
                    send_message_v1(f"{round(axis_x,3)} {round(axis_y,3)} {round(axis_z,3)}")
                    print("X: ", round(-axis_x,3), "  Y: ", round(axis_y*0.5,3), "  Z: ", round(axis_z*100,3))
                    

    except KeyboardInterrupt:
        ep_robot.close()

        pygame.quit()