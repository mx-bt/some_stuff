import pyautogui
import time
import random

def move_mouse():
    # Get the current mouse position
    current_x, current_y = pyautogui.position()

    # Generate random offsets for x and y coordinates
    offset_x = random.randint(-20, 20)  # Random integer between -20 and 20
    offset_y = random.randint(-20, 20)  # Random integer between -20 and 20

    # Move the mouse with the random offsets
    pyautogui.moveTo(current_x + offset_x, current_y + offset_y)

    # Optionally, move the mouse back to the original position
    # pyautogui.moveTo(current_x, current_y)

# Main loop to move the mouse every 5 seconds
while True:
    move_mouse()
    time.sleep(5)