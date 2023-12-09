import pygame
import time
from robomaster import robot, camera, robotic_arm

# Initialisiere den RoboMaster EP
ep_robot = robot.Robot()
ep_robot.initialize(conn_type="ap")
ep_camera = ep_robot.camera
ep_arm = ep_robot.robotic_arm

ep_camera.start_video_stream(display=True, resolution=camera.STREAM_720P)

# Initialisiere den Joystick
pygame.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

try:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                # Lese die Joystick-Achsen und sende Befehle an den Roboter
                axis_x = joystick.get_axis(1)
                axis_y = joystick.get_axis(0)
                axis_z = joystick.get_axis(3)
                axis_armx = joystick.get_axis(4)
                #axis_army = joystick.get_axis(5)
                print("X: ", round(axis_x), "  Y: ", round(axis_y), "  Z: ", round(axis_z))
                ep_robot.chassis.drive_speed(x=-axis_x,y=axis_y*0.5,z=axis_z*100,timeout=0)
                #ep_arm.move(x=axis_armx, y=0)

except KeyboardInterrupt:
    # Beende das Programm und schließe die Verbindung zum RoboMaster EP
    ep_camera.stop_video_stream()
    ep_robot.close()
    pygame.quit()
