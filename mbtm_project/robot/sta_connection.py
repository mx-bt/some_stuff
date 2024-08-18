
import time
import robomaster
from robomaster import conn
from MyQR import myqr
from PIL import Image

"""
INSTRUCTIONS:
1. modify info
2. run program
3. scan qrcode with robomaster camera
"""

QRCODE_NAME = "qrcode.png"
helper = conn.ConnectionHelper()
info = helper.build_qrcode_string(ssid="NutellagoesWITHbutter", password="Wifi_key_1337_!") # (ssid="log-robo", password="by2qhDwQORXnQZFN6Xwf")
# (ssid="NutellagoesWITHbutter", password="Wifi_key_1337_!")
myqr.run(words=info) 
time.sleep(1)
img = Image.open(QRCODE_NAME)
img.show()
###
 
