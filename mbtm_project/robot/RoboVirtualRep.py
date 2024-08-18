import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
import json

# the following imports are needed for the custom functions
# they are rather imported than pasted here to enable separate analysis of battery life (e.g., plotting)
from battery_simulation import battery_life_fix, battery_life_linear_reg # Custom functions

plt.style.use("fivethirtyeight")

# conda activate robomaster-environment
# cd C:\Users\Max\Documents\MOM\ws2324\mbtm_dz_showcase
# python RoboVirtualRep.py

def animate(i):
    """
    This function is called every 200ms to update the plot
    It reads the data from the csv files and plots it in real time
    """
    try:
        # Clear old values
        plt.cla()

        # Reading the csv files
        xyz_data = pd.read_csv(r"C:\Users\Max\Documents\MOM\ws2324\mbtm_dz_showcase\xyz_data.csv")
        battery_data = pd.read_csv(r"C:\Users\Max\Documents\MOM\ws2324\mbtm_dz_showcase\battery_data.csv")
        
        # Get the current robot trayectory and orientation
        # For more convenience, the x and y values are swapped (this does not interfere with any calculation)
        y_trayectory = xyz_data["x_value"]
        x_trayectory = xyz_data["y_value"] 
        

        # Plot the robot trajectory
        # plt.plot(x_trayectory, y_trayectory, label='Trajectory', color='blue', zorder=2)
        
        # Retrieving the route data
        with open('astar_path_data.json', 'r') as json_file:
            loaded_data = json.load(json_file)
            loaded_route_x = loaded_data['route_x']
            loaded_route_y = loaded_data['route_y']
            # print("TEST MARKER", len(loaded_route_x))

            # Chck if a route exists
            if len(loaded_route_x) != 0:
                route_exists = True
                route_x_scaled = [float(value) / 100 for value in loaded_route_x]
                route_y_scaled = [float(value) / 100 for value in loaded_route_y]
                destination_x = route_x_scaled[0]
                destination_y = route_y_scaled[0]
                plt.plot(route_x_scaled, route_y_scaled, "-r", label="Planned Path", alpha=0.3)
            else:
                # If no route exists, set the destination to False
                # this is needed to enable further code functionality
                destination_x, destination_y = False, False
                route_exists = False

        # Get the current robot x and y position and orientation
        robot_live_pos_x = x_trayectory.tail(1).values[0]
        robot_live_pos_y = y_trayectory.tail(1).values[0]
        z_angle = xyz_data["z_value"].tail(1).values[0]

        # Plot the robot position using an image, rotate it, transform it to the right size and add it to the plot
        robot_img = Image.open('graphical_reps\Roboter.png')
        rotated_robot_img = robot_img.rotate(-z_angle)
        plot_size = min(plt.gcf().get_size_inches())
        zoom_factor = 0.025 * plot_size
        imagebox = OffsetImage(rotated_robot_img, zoom=zoom_factor, resample=True)

        # Add the robot image to the plot
        ab = AnnotationBbox(imagebox, (robot_live_pos_x, robot_live_pos_y), frameon=False, pad=0)
        plt.gca().add_artist(ab)

        # Define the plot size and background image
        field_size = 4 #m
        background_img = plt.imread('graphical_reps\warehouse_map.jpg')
        plt.imshow(background_img, extent=[0, field_size, 0, field_size])

        # Battery life approximation using DJI values
        current_battery_percentage = battery_data["battery_percentage"].tail(1).values[0]
        standby_pred, usage_pred = battery_life_fix(current_battery_percentage)
        standby_pred, usage_pred = round(standby_pred), round(usage_pred)

        # Display the battery life approximation as text boxes next to the plot
        bbox_pos_x = 1.1
        plt.text(bbox_pos_x, 1.0, f'Battery: {current_battery_percentage}%', transform=plt.gca().transAxes, ha='left', va='top',
                 bbox=dict(boxstyle='round,pad=0.3', edgecolor='blue', facecolor='lightblue'))
        
        plt.text(bbox_pos_x, 0.9, f'Battery life max: {standby_pred} min', transform=plt.gca().transAxes, ha='left', va='top',
                 bbox=dict(boxstyle='round,pad=0.3', edgecolor='blue', facecolor='lightblue'))
        
        plt.text(bbox_pos_x, 0.8, f'Battery life min: {usage_pred} min', transform=plt.gca().transAxes, ha='left', va='top',
                 bbox=dict(boxstyle='round,pad=0.3', edgecolor='blue', facecolor='lightblue'))
        
        # Battery life approximation using linear regression
        statistical_approx = battery_life_linear_reg()
        sa_display = standby_pred if statistical_approx > standby_pred else statistical_approx
        
        if len(battery_data["battery_percentage"].tolist()) > 60: # only display if enough data is available
            plt.text(bbox_pos_x, 0.7, f'Battery life statistical: {sa_display} min', transform=plt.gca().transAxes, ha='left', va='top',
                    bbox=dict(boxstyle='round,pad=0.3', edgecolor='blue', facecolor='lightblue'))
        else:
            pass    
        
        plt.ylim(0, field_size)  # Set y-axis limits
        plt.xlim(0, field_size)  # Set x-axis limits
        plt.xlabel('x (m)')
        plt.ylabel('y (m)')
        plt.title('Real Time Robot Position')

        # adapt the legend
        if route_exists:
            plt.legend(["Planned Path"], loc='upper left',bbox_to_anchor=(-0.5, 1)) # "Trajectory", 
        else:
           # plt.legend(["Trajectory"], loc='upper left', bbox_to_anchor=(-0.5, 1))
            pass

        # delete path if robot has reached the destination +/- 0.1m
           
        if destination_x:
            print(f"Live pos: {robot_live_pos_x, robot_live_pos_y} Goal: {destination_x, destination_y}")
            if (round(robot_live_pos_x,1) == round(destination_x,1)) and (round(robot_live_pos_y,1) == round(destination_y,1)):
                print("Goal reached. Deleted old path")
                with open('astar_path_data.json', 'w') as json_file:
                    json.dump({'route_x': [], 'route_y': []}, json_file)

    # Use Ctrl+C to stop the program
    except KeyboardInterrupt:
        plt.close()
        raise

# Start the animation with a frequency of 5 Hz
ani = FuncAnimation(plt.gcf(), animate, interval=200)
plt.tight_layout()
plt.show()
