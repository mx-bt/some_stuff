"""
Robomaster EP Core Operating System
Subject focus: MBTM Project "Greenfield Digital Twin"

Note: 
- this code is based on the Robomaster EP SDK and some more common Python libraries
- it is centered to fulfill real time tracking and data collection from its sensors
- however, there are a lot of function that are not crucial for the project, but
    helped to create a common understanding of the robot's functionalities and a more
    enjoyable experience
- the code is not optimized for speed or memory usage, but for readability, 
    maintainability and scalability to include more functionalities easily (important
    for later Digital Twin development)

Working Functionality:
- driving with joystick
- arm and gripper movement with joystick
- route tracking and live strean (use separate file: animated_plot.py)
- computer vision for persons and robots
- optional ap and sta connection
- some testing functionalities for precision testing
- optional fun mode
- fetching route data from a json file and execute it autonomously

Counterintuitive key features for functionality:
- stabilizes itself when not moving
- gripper status detection
- 5 different arm positions
- optionally records all session data
"""

import pygame # for joystick
from robomaster import robot, camera # the robomaster SDK
import pandas as pd # for data handling
import numpy as np # for data handling and numerical operations
import csv # for csv file handling
import threading # for parallel processing
import cv2 # for computer vision
import math
import time
import json

# Configuration
sta_connection = True # choose between "sta" and "ap"
activate_CV = False  # choose between "cv" and "no_cv"
activate_live_tracking = True
fun_mode = False 
video_stream = False

# Initialize RoboMaster EP
ep_robot = robot.Robot()

if sta_connection == True:
    # make sure that the robot is connected to the same network as the computer
    try:
        ep_robot.initialize(conn_type="sta", sn="3JKCK7W0030DCD")
    except Exception:
        ep_robot.close()
        print("Robot not correctly connected")
else:
    ep_robot.initialize(conn_type="ap")

# Version check
ep_version = ep_robot.get_version()
print(f"Robot Version {ep_version}")


if ep_version == None:
    ep_robot.close()
    print("Robot not correctly connected")
else:
    # Initializing chassis, camera, arm, gripper and battery
    ep_chassis = ep_robot.chassis
    ep_camera = ep_robot.camera
    ep_arm = ep_robot.robotic_arm
    ep_gripper = ep_robot.gripper
    ep_battery = ep_robot.battery

    # Iniiating joystick
    pygame.init()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    # Initializing variables for live tracking and gripper functionality
    all_info = np.empty((0, 6), dtype=int)
    t_v = np.array([])
    gripper_status = str()
    current_gripper_action = str()


# ==============================================================
# CV Functionality
# ==============================================================
if activate_CV == True:

    # Initialize computer vision
    ep_vision = ep_robot.vision

    class PersonInfo:

        """
        This class is provided by RoboMaster EP SDK
        It creates a person object to manage the CV data:
        - x,y: center of the detected person
        - w,h: width and height of the detected person
        """

        def __init__(self, x, y, w, h):
            self._x = x
            self._y = y
            self._w = w
            self._h = h

        @property
        def pt1_person(self):
            return int((self._x - self._w / 2) * 1280), int((self._y - self._h / 2) * 720)

        @property
        def pt2_person(self):
            return int((self._x + self._w / 2) * 1280), int((self._y + self._h / 2) * 720)

        @property
        def center_person(self):
            return int(self._x * 1280), int(self._y * 720)
    persons = []

    class RobotInfo:

        """
        This class is provided by RoboMaster EP SDK
        It creates a robot object to manage the CV data:
        - x,y: center of the detected robot
        - w,h: width and height of the detected robot
        """

        def __init__(self, x, y, w, h):
            self._x = x
            self._y = y
            self._w = w
            self._h = h

        @property
        def pt1_robot(self):
            return int((self._x - self._w / 2) * 1280), int((self._y - self._h / 2) * 720)

        @property
        def pt2_robot(self):
            return int((self._x + self._w / 2) * 1280), int((self._y + self._h / 2) * 720)

        @property
        def center_robot(self):
            return int(self._x * 1280), int(self._y * 720)
    robots = []

    cv_lock = threading.Lock()

    def on_detect_persons(person_info):

        global persons

        with cv_lock:
            num_persons = len(person_info)
            persons.clear()
            for i in range(0, num_persons):
                x, y, w, h = person_info[i]
                persons.append(PersonInfo(x, y, w, h))
                # print("person: x:{0}, y:{1}, w:{2}, h:{3}".format(x, y, w, h))

    def on_detect_robots(robots_info):

        global robots

        with cv_lock:
            num_robots = len(robots_info)
            robots.clear()
            for i in range(0, num_robots):
                x, y, w, h = robots_info[i]
                robots.append(RobotInfo(x, y, w, h))
                # print("robot: x:{0}, y:{1}, w:{2}, h:{3}".format(x, y, w, h))

    def process_and_display_image(ep_camera, robots): #persons,
        try: 
            while True:
                img = ep_camera.read_cv2_image(strategy="newest", timeout=5)
                with cv_lock:
                    for r in range(0, len(robots)):
                        pt1_robot = robots[r].pt1_robot
                        pt2_robot = robots[r].pt2_robot
                        cv2.rectangle(img, pt1_robot, pt2_robot, (255, 255, 255))

                        text = f"Robot {r+1}"
                        org = (pt1_robot[0], pt2_robot[1] - 10)  # Position the text slightly above the bounding box
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        font_scale = 0.5
                        font_thickness = 1
                        cv2.putText(img, text, org, font, font_scale, (255, 255, 255), font_thickness, cv2.LINE_AA)

                    # for p in range(0, len(persons)):
                    #     pt1_person = persons[p].pt1_person
                    #     pt2_person = persons[p].pt2_person
                    #     cv2.rectangle(img, pt1_person, pt2_person, (255, 255, 255))
                        
                    #     text = f"Person {p+1}"
                    #     org = (pt1_person[0], pt2_person[1] - 10)  # Position the text slightly above the bounding box
                    #     font = cv2.FONT_HERSHEY_SIMPLEX
                    #     font_scale = 0.5
                    #     font_thickness = 1
                    #     cv2.putText(img, text, org, font, font_scale, (255, 255, 255), font_thickness, cv2.LINE_AA)

                    cv2.imshow("computer_vision_robot", img)
                    cv2.waitKey(10)
        except KeyboardInterrupt:
            pass
        finally:
            cv2.destroyAllWindows()

    ep_camera.start_video_stream(display=False)
    cv_result_robot = ep_vision.sub_detect_info(name="robot", callback=on_detect_robots)
    # cv_result_person = ep_vision.sub_detect_info(name="person", callback=on_detect_persons)
    # create thread
    image_thread = threading.Thread(target=process_and_display_image, args=(ep_camera, robots)) #robots,persons,
    # Start the thread
    image_thread.start()
elif activate_CV == False:
    if video_stream == True:
        ep_camera.start_video_stream(display=True, resolution=camera.STREAM_720P)
    else:
        pass
    pass
else:
    ep_robot.close()
    pygame.quit()
    print("activate_CV must be either True or False")

# ==============================================================
# Testing Functionalities
# ==============================================================
def testing_rectangle_1():
    """
    The goal of this test is to keep the robot moving in a rectangle
    This was used to test battery exhaustion
    """
    distance = 1
    xy_speed = 1
    for _ in range(0, 256):
        ep_chassis.move(y=-distance,xy_speed=xy_speed).wait_for_completed()
        ep_chassis.move(x=-distance,xy_speed=xy_speed).wait_for_completed()
        ep_chassis.move(y=distance,xy_speed=xy_speed).wait_for_completed()
        ep_chassis.move(x=distance,xy_speed=xy_speed).wait_for_completed()

def testing_rectangle_2():
    """
    The goal of this test is to keep the robot moving in a rectangle
    This was used to test battery exhaustion
    """
    xy_speed = 1
    distance = 0.5
    z_speed = 90
    for _ in range(0,4):
        for _ in range(0, 4):
            ep_chassis.move(z=-90,z_speed=z_speed).wait_for_completed()
            ep_chassis.move(x=distance,xy_speed=xy_speed).wait_for_completed()

# ==============================================================´
# Live Tracking Functionalities
# ==============================================================
if activate_live_tracking == True:

    with open('battery_data.csv', 'w') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=["battery_percentage"])
        csv_writer.writeheader()

    def sub_info_handler(batter_info, ep_robot):
        """
        This function receives the battery percentage and writes it to a csv file
        """
        percent = batter_info
        # print(f"Battery: {percent}%.")
        with open('battery_data.csv', 'a') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=["battery_percentage"])
            info = {
                "battery_percentage": percent,
            }
            csv_writer.writerow(info)

    # Subscribing to the battery information with a frequency of 1 Hz
    ep_battery.sub_battery_info(1, sub_info_handler, ep_robot)

    # init the csv
    with open('xyz_data.csv', 'w') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=["x_value", "y_value", "z_value"])
        csv_writer.writeheader()

    # Subscribe to chassis location and attitude information
    def sub_position_handler(position_info):
        """
        This function receives the chassis position
        """
        global t_v
        x_v, y_v, z_v = position_info
        x_v, y_v, z_v = round(x_v,2), round(y_v,2), round(z_v,2)
        t_v = np.array([])
        t_v = np.append(t_v,[x_v,y_v,z_v])
        # print(f"chassis position: x:{x_v}, y:{y_v}")

    # Subscribing to the chassis position information with a frequency of 5 Hz
    ep_chassis.sub_position(freq=5, callback=sub_position_handler)

    def sub_attitude_info_handler(attitude_info):
        """
        This function receives the chassis attitude information
        It combines with the chassis position and writes it to a csv file
        This forms the base of the live tracking
        """
        global all_info
        global t_v
        yaw, pitch, roll = attitude_info
        # print("Yaw angle = ", yaw)
        yaw, pitch, roll = round(yaw,2), round(pitch,2), round(roll,2)
        t_v = np.append(t_v,[yaw, pitch, roll])
        # print(f"x={t_v[0]} y={t_v[1]} z/yaw={t_v[3]} pitch={t_v[4]} roll={t_v[5]}")
        all_info = np.append(all_info, [t_v], axis=0)

        with open('xyz_data.csv', 'a') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=["x_value", "y_value", "z_value"])
            info = {
                "x_value": t_v[0],
                "y_value": t_v[1],
                "z_value": yaw,
            }
            csv_writer.writerow(info)
    
    # Subscribing to the chassis attitude information with a frequency of 5 Hz
    ep_chassis.sub_attitude(freq=5, callback=sub_attitude_info_handler)
else:
    pass    

# subscribe to gripper data (!)
def gripper_data_handler(grip_stat_info):
    "this has functional necessity for the grippper to work"
    global gripper_status
    gripper_status= grip_stat_info
ep_gripper.sub_status(freq=5, callback=gripper_data_handler)

# ==============================================================
# Automated Route Driving Functionality
# ==============================================================

def angle_calc(movement_vector: tuple) -> int:
    e = 0.00001 # to avoid illegal math operations
    vector_angle = math.degrees(math.atan((movement_vector[0]+e)/(movement_vector[1]+e)))
    x_value = movement_vector[0]
    y_value = movement_vector[1]

    # adapt angle depending on the vector quadrant
    if (x_value >= 0) and (y_value < 0):
        vector_angle += 180
    elif (x_value < 0) and (y_value >= 0):
        vector_angle += 360
    elif (x_value < 0) and (y_value < 0):
        vector_angle += 180
    else:
        pass    
    # print(round(vector_angle),"°")

    return int(round(vector_angle))

def adjust_angle(current_angle: int, target_angle: int) -> int:

    angle_difference = target_angle - current_angle

    # choose shortest possible adaption
    if angle_difference > 180:
        angle_difference -= 360
    elif angle_difference < -180:
        angle_difference += 360
    else:
        pass

    return int(angle_difference)

def path_to_movement(current_z: int = 0):

    # Get the routes
    with open('astar_path_data.json', 'r') as json_file:
            loaded_data = json.load(json_file)
            loaded_route_x = loaded_data['route_x']
            loaded_route_y = loaded_data['route_y']
            x_scaled = [float(value) / 100 for value in loaded_route_x]
            y_scaled = [float(value) / 100 for value in loaded_route_y]
            x_scaled.reverse()
            y_scaled.reverse()

    live_angle = current_z # replace with yaw/z value
    # print("Current Z Position ", live_angle)

    x_r = []
    y_r = []
    z_r = []

    for i in range(0, len(x_scaled)-1):
        # print(small_test_path[i])  
        
        movement_vector = (round(x_scaled[i+1]-x_scaled[i],1), round(y_scaled[i+1]-y_scaled[i],1)) # create vector tuple 
        # print(f"Movement vector {i}: ", movement_vector[0], movement_vector[1])
        vector_angle = angle_calc(movement_vector)
        # print("First Z direction ", vector_angle) if i == 0 else None # some more testing
        
        angle_adjustment = adjust_angle(live_angle, vector_angle)
        # print(f"current angle {live_angle}° target angle {vector_angle}° resulting adjustment {angle_adjustment}°")
        live_angle += angle_adjustment

        x_vec = movement_vector[0]
        y_vec = movement_vector[1]
        x_r.append(x_vec)
        y_r.append(y_vec)
        z_r.append(-angle_adjustment) # ANGLE IS ADAPTED HERE !

    x_movez = []
    y_movez = []
    z_movez = []

    # Flattingways: accumulates even parts of the route
    m = 0 # Init the artificial index
    a_move = [0,0,0]
    while m <= (len(z_r)-1):
            # print(m)
            # Initiate current move [X,Y,Z]
            a_move[0] = x_r[m] # synchronize first move x
            a_move[1] = y_r[m] # synchronize first move y
            a_move[2] = z_r[m] # synchronize first move z
            # print(f"Move {m} raw: ", round(a_move[0],1), round(a_move[1],1), a_move[2])
            if m == (len(z_r)-1): # if last move and stil available
                x_movez.append(round(a_move[0],1))
                y_movez.append(round(a_move[1],1))
                z_movez.append(a_move[2])
                m += 1
            elif z_r[m+1] == 0: # if no angle is adpated in the next move
                while z_r[m+1] == 0: # while the above condition is true
                    a_move[0] += x_r[m+1] # accumulate x value # was m before
                    a_move[1] += y_r[m+1] # accumulate y value # was m before
                    if m+1 == (len(z_r)-1): # if last move
                        m += 1
                        break
                    else:
                        m += 1
                    # increase index to keep iterating
                x_movez.append(round(a_move[0],1))
                y_movez.append(round(a_move[1],1))
                z_movez.append(a_move[2])
                m += 1
            else:
                if int(m) != int(len(z_r)-1): # if not last move
                    x_movez.append(round(a_move[0],1))
                    y_movez.append(round(a_move[1],1))
                    z_movez.append(a_move[2])
                    m += 1 # increase index to move on to next move
                else:
                    pass

    xy_speed = 0.75 # limit speed to avoid slipping
    z_speed = 90 # limit turning speed speed to avoid slipping


    # print("First Z adjustment ", z_movez[0])

    for m in range(len(x_movez)):
        x_move = round(math.sqrt(x_movez[m]**2 + y_movez[m]**2),2)
        # First turn, then move
        ep_chassis.move(z=z_movez[m], z_speed=z_speed).wait_for_completed()
        # # time.sleep(0.5) # for testing, 1.1 for rough correction of the distance
        ep_chassis.move(x=x_move*1.1, y=0, xy_speed=xy_speed).wait_for_completed()


# ==============================================================
# Main Loop for steering and command receipt
# ==============================================================

try:
    while True:
        # try: # some testing functionality for fetching the robot angle during operation
        #     print(all_info[-1][-3])
        # except IndexError:
        #     pass
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION or event.type == pygame.JOYHATMOTION or event.type == pygame.JOYBUTTONDOWN:
                pygame.event.pump()
                # Converting joystick input into axis information
                axis_x = joystick.get_axis(1)
                axis_y = joystick.get_axis(0)
                axis_z = joystick.get_axis(3)

                # The robot stabilizes itself when not moving and receiving minor inputs
                axis_x, axis_y, axis_z = round(axis_x,2), round(axis_y,2), round(axis_z,2)

                # With a special button, the robot can be moved smoother
                scaler = 0.2 if joystick.get_button(0) else 1

                # Convert axis and scaler input to robot movement
                ep_robot.chassis.drive_speed(x=-axis_x*scaler,y=axis_y*0.5*scaler,z=axis_z*100*scaler,timeout=0)

                # The fun mode allows to play sounds instead of the test drives
                if fun_mode == True:
                    ep_robot.play_audio(filename=r"sounds\final_countdown.wav") if joystick.get_button(5) else None
                    ep_robot.play_audio(filename=r"sounds\mexican_hat_dance.wav") if joystick.get_button(6) else None
                else:
                    # Functionality described in the testing section
                    testing_rectangle_1() if joystick.get_button(5) else None # Real button nr = 6
                    testing_rectangle_2() if joystick.get_button(6) else None # Real button nr = 7

                    # Initiate the route execution
                    try:
                        current_robot_angle = int(round((all_info[-1][-3])))
                    except IndexError:
                        pass
            
                    if joystick.get_button(7): # Real button nr = 8
                        current_robot_angle_picker = current_robot_angle
                        path_to_movement(current_robot_angle_picker)
                        time.sleep(2)
                    else:
                        None 


                # Retrieve hat position from joystick
                j_hat = round(joystick.get_hat(0)[1])

                # Move arm and gripper with joystick
                ep_arm.move(x=j_hat*180, y=(-1)*j_hat*110).wait_for_completed() if abs(j_hat) == 1 else None

                # Execute recentering movement
                ep_arm.recenter().wait_for_completed() if joystick.get_button(1) == 1 else None

                if joystick.get_button(3) or joystick.get_button(4):
                    if joystick.get_button(3):
                        current_gripper_action = "closing..."
                        ep_gripper.close(power=100)
                    elif joystick.get_button(4):
                        current_gripper_action = "opening..."
                        ep_gripper.open(power=100)
                    else:
                        pass
                else:
                    current_gripper_action = "chilling..."
                    pass

# ==============================================================
# Exit Program and unsubscribe all subscriptions
# ==============================================================

except KeyboardInterrupt: # End the complete program properly with Ctrl + C

    if activate_CV == True:
        result = ep_vision.unsub_detect_info(name="robot") # CV
        cv2.destroyAllWindows() # CV 2
    if activate_live_tracking == True:
        # The code below can be used to save the live tracking data to a csv file
        # print("All Data: ", all_info)
        # main_df = pd.DataFrame(all_info, columns = ['x', 'y', 'z', 'yaw', 'pitch', 'roll'])
        # main_df.to_csv('all_data_history.csv', index=False)
        # print("Dataframe: ", main_df)
        ep_chassis.unsub_attitude()
        ep_chassis.unsub_position()
    
    ep_gripper.unsub_status()
    ep_camera.stop_video_stream()
    ep_battery.unsub_battery_info()

    ep_robot.close()
    pygame.quit()