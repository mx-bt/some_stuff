import math
import json
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

    print("X_orig: ", x_scaled)
    print("Y_orig: ", y_scaled)
    print("lens: ", len(x_scaled), len(y_scaled), len(x_scaled))
    print("")
    print("X_r: ", x_r)
    print("Y_r: ", y_r)
    print("Z_r: ", z_r)
    print("lens: ", len(x_r), len(y_r), len(z_r))
    print("")

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
    
    print("")
    print("X: ", x_movez)
    print("Y: ", y_movez)
    print("Z: ", z_movez)  
    print("lens: ", len(x_movez))

path_to_movement(-1.2)