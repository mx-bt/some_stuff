import pygame
import time
from robomaster import robot, camera, robotic_arm
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime
import time
import pandas as pd
import numpy as np

# Initialize RoboMaster EP
ep_robot = robot.Robot()
ep_robot.initialize(conn_type="ap")

# Establishing robot connection

version_ = ep_robot.get_version()
print(f"Robot Version {version_}")

if version_ == None:
    ep_robot.close()
else:
    # Initializing chassis, camera, joystick
    ep_chassis = ep_robot.chassis
    ep_camera = ep_robot.camera
    ep_camera.start_video_stream(display=True, resolution=camera.STREAM_720P)
    pygame.init()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    pass

all_info = np.empty((0, 6), dtype=int) # all information list
i = 0
t_v = np.array([])

# Subscribe to chassis location information

def sub_position_handler(position_info):

    global temp_values
    x, y, z = position_info
    x, y, z = round(x,2), round(y,2), round(z,2)

    t_v = np.array([])
    t_v = np.append(t_v,[x,y,z])
    # print(f"chassis position: x:{x}, y:{y}, z:{z}")

def sub_attitude_info_handler(attitude_info):

    global i
    global all_info
    global t_v

    yaw, pitch, roll = attitude_info
    yaw, pitch, roll = round(yaw,2), round(pitch,2), round(roll,2)

    t_v = np.append(t_v,[yaw, pitch, roll])
    print(t_v[0],t_v[1],t_v[2],t_v[3],t_v[4],t_v[5])

    all_info = np.append(all_info, [[yaw, pitch, roll]], axis=0)

    # print(ail[i][0],ail[i][1],ail[i][2],ail[i][3],ail[i][4],ail[i][5])
    # print(f"chassis attitude: yaw:{yaw}, pitch:{pitch}, roll:{roll} ")
    # i += 1

ep_chassis.sub_position(freq=1, callback=sub_position_handler)
ep_chassis.sub_attitude(freq=1, callback=sub_attitude_info_handler)

try:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                # Lese die Joystick-Achsen und sende Befehle an den Roboter
                axis_x = joystick.get_axis(1)
                axis_y = joystick.get_axis(0)
                axis_z = joystick.get_axis(3)
                # axis_armx = joystick.get_axis(4)
                #axis_army = joystick.get_axis(5)
                # print("X: ", round(axis_x), "  Y: ", round(axis_y), "  Z: ", round(axis_z))
                ep_robot.chassis.drive_speed(x=-axis_x,y=axis_y*0.5,z=axis_z*100,timeout=0)
                #ep_arm.move(x=axis_armx, y=0)

# Stop the program (Ctrl+C) and end subscriptions
except KeyboardInterrupt:
    main_df = pd.DataFrame(all_info, columns = ['x', 'y', 'z', 'yaw', 'pitch', 'roll'])
    main_df.to_csv('positional_data.csv', index=False)
    
    ep_chassis.unsub_position()
    ep_camera.stop_video_stream()
    ep_robot.close()
    pygame.quit()
