from a_star_planner import AStarPlanner
import matplotlib.pyplot as plt
import cv2
import json
import pandas as pd

# conda activate robomaster-environment
# cd C:\Users\Max\Documents\MOM\ws2324\mbtm_dz_showcase
# python RoutePlanningAStar.py

def route_planning(target_coordinates, start_coordinates):

    image_path = r"C:\Users\Max\Documents\MOM\ws2324\mbtm_dz_showcase\graphical_reps\maze.jpg"
    # Bild wird mit Hilfe einer visuellen Allokationsplattform für Rastergrafik-Inkorporation erstellt


    def convert_image_to_coordinates(image_path):
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE) # Read the image
        height, width = img.shape[:2] 

        _, thresh = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY) # Threshold the image to convert it to black and white
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE) # Find contours in the binary image

        obstacle_coordinates = []
        for i, contour in enumerate(contours): # Extract coordinates from contours
            for point in contour:
                obstacle_coordinates.append(tuple((point[0][0], height-point[0][1]))) # Flip the y-axis
        return obstacle_coordinates
    

    obstacle_coordinates = convert_image_to_coordinates(image_path)

    try:
        # Define start and goal positions
        start_x, start_y = start_coordinates[0], start_coordinates[1]  # Start position
        goal_x, goal_y = target_coordinates[0], target_coordinates[1] # Goal position

        # Set up obstacle positions
        obstacles_x, obstacles_y = [], []
        for i in range(len(obstacle_coordinates)):
            obstacles_x.append(obstacle_coordinates[i][0])
            obstacles_y.append(obstacle_coordinates[i][1])

        # Plot the environment
        # plt.plot(obstacles_x, obstacles_y, ".k", label="Obstacles")
        # plt.plot(start_x, start_y, "og", label="Start")
        # plt.plot(goal_x, goal_y, "xb", label="Goal")
        # plt.grid(True)
        # # plt.axis("equal")
        # plt.legend()
        # plt.title("Simple Path Planning with A*")

        # Initialize A* planner
        grid_size = 10  # Grid resolution
        robot_radius = 20 # Robot radius

        # Perform path planning
        a_star = AStarPlanner(obstacles_x, obstacles_y, grid_size, robot_radius)
        route_x, route_y = a_star.planning(start_x, start_y, goal_x, goal_y)

        if route_x is None or route_y is None:
            print("")
            print("Route calculation not possible.")
            print("Please choose new destination.")
            print("")
            # empty json file
            with open('astar_path_data.json', 'w') as json_file:
                json.dump({'route_x': [], 'route_y': []}, json_file)
        
            return None

        else:
            print("")
            print("Route calculated:")
            route_astar = []
            for i in range(len(route_x)):
                route_astar.append((route_x[i], route_y[i])) 
            route_astar.reverse()

            with open('astar_path_data.json', 'w') as json_file:
                json.dump({'route_x': list(route_x), 'route_y': list(route_y)}, json_file)

            print(route_astar)

            background_img = plt.imread('graphical_reps\warehouse_map_2.jpg')
            height, width, _ = background_img.shape
            # plt.imshow(background_img, extent=[0, width, 0, height])

            # # Plot the planned path
            # plt.plot(route_x, route_y, "-r", label="Planned Path", alpha=0.3)

            # plt.legend()
            # plt.show()

    except Exception as e:
        # Handle the exception (print an error message)
        print(f"Error in the process: {e}")
        return None

    return route_astar

# init an empty json file
with open('astar_path_data.json', 'w') as json_file:
    json.dump({'route_x': [], 'route_y': []}, json_file)

while True:
    try:
        print("")
        str_in = input("Target coordinates (like: 'x y')(cm): ")
        if str_in == "delete":
            with open('astar_path_data.json', 'w') as json_file:
                json.dump({'route_x': [], 'route_y': []}, json_file)
            print("")
            print("Current route deleted.")
            continue
        else:
            target_x, target_y = str_in.split(" ")
            target = (int(target_x),int(target_y))

        # Set current robot position as start
        location_data_file = r"C:\Users\Max\Documents\MOM\ws2324\mbtm_dz_showcase\xyz_data.csv"
        xyz_data = pd.read_csv(location_data_file)
        current_pos_y = xyz_data["x_value"].tail(1).values[0]
        current_pos_x = xyz_data["y_value"].tail(1).values[0]
        #
        start = (int(float(current_pos_x)*100), int(float(current_pos_y)*100))

        sp = route_planning(target, start)
 
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        break   

print("clean program end")
