import threading
from dobot_api import DobotApiDashboard, DobotApi, DobotApiMove, MyType
from time import sleep
import numpy as np
import time
from ObjetColor import ColorDetector


detector = ColorDetector()
Width, Height = 550,700
Enable=True
color = None
current_actual = None
point_Init = [223.74, 0, 41.13, 0 ,0 ,0]

posis = [239.591208, 0.161717, -166.945007, 49.317848, 0.000000, 0.000000]
pointMemory = []


calibracion = False

def connect_robot():
    try:
        ip = "192.168.0.12"
        dashboard_p = 29999
        move_p = 30003
        feed_p = 30004
        dashboard = DobotApiDashboard(ip, dashboard_p)
        move = DobotApiMove(ip, move_p)
        feed = DobotApi(ip, feed_p)
        print(">.<conexión exitosa>!<")

        
        return dashboard, move, feed
    except Exception as e:
        print(":(La conexión falló:(")
        raise e
connect_robot()