import threading
from dobot_api import DobotApiDashboard, DobotApi, DobotApiMove, MyType
from time import sleep
import numpy as np
import keyboard
import time
from ObjetColor import ColorDetector


detector = ColorDetector()
Width, Height = 550,700
Enable=True
color = None
current_actual = None
point_Init = [248.34, 4.55, 0.9, 33.8 ,0 ,0]

posis = [248, 4, 0, 33,0 ,0]
posis2 = [248, 4, 0, 33,0,0]
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

def run_point(move: DobotApiMove, point_list: list):
    move.MovL(point_list[0], point_list[1], point_list[2], point_list[3],point_list[4],point_list[5])

def get_feed(feed: DobotApi):
    global current_actual
    hasRead = 0
    while True:
        data = bytes()
        while hasRead < 1440:
            temp = feed.socket_dobot.recv(1440 - hasRead)
            if len(temp) > 0:
                hasRead += len(temp)
                data += temp
        hasRead = 0

        a = np.frombuffer(data, dtype=MyType)
        if hex((a['test_value'][0])) == '0x123456789abcdef':

            # Refresh Properties
            current_actual = a["tool_vector_actual"][0]
            #print(point_Init)
            #print("tool_vector_actual:", current_actual)

        sleep(0.001)

def wait_arrive(point_list):
    global current_actual
    while True:
        is_arrive = True

        if current_actual is not None:
            for index in range(4):
                if (abs(current_actual[index] - point_list[index]) > 1):
                    print("verificAda 1")
                    is_arrive = False

            if is_arrive:
                return

        sleep(0.001)

def increase_x_coordinate():
    global point_Init
    point_Init[0] += 1
 
def decrease_x_coordinate():
    global point_Init
    point_Init[0] -= 1

def increase_y_coordinate():
    global point_Init
    point_Init[1] += 1
 
def decrease_y_coordinate():
    global point_Init
    point_Init[1] -= 1

def increase_z_coordinate():
    global point_Init
    point_Init[2] += 1
 
def decrease_z_coordinate():
    global point_Init
    point_Init[2] -= 1  

def ola():    
    global point_Init, move
    run_point(move, point_Init)
    wait_arrive(point_Init)

           
def ActivarRobot(dashboard: DobotApiDashboard, feed):
    global Enable
    if(Enable):
        ola = dashboard.EnableRobot()
        feed_thread = threading.Thread(target=get_feed, args=(feed,))
        feed_thread.setDaemon(True)
        feed_thread.start()

        

        if(ola[0]=="0"):
            print("se habilito con Exito")
            Enable=False
        else:
            print("no se pudo habilitar")
    else:
     
        ola=dashboard.DisableRobot()
       
        if(ola[0]=="0"):
            print("se deshabilito con Exito")
            Enable=True
        else:
            print("no se pudo deshabilitar")
        
def EliminarAlarma(dashboard):
    dashboard.ClearError()
def ConnectRobot():
     
    dashboard, move, feed = connect_robot()
    return dashboard, move, feed
def StopEmergency(dashboard: DobotApiDashboard):
    dashboard.EmergencyStop()
    print("parada de emergencia")
dashboard, move, feed = connect_robot()
posicionActual=None
while True:
    keyboard.add_hotkey('*', lambda:StopEmergency(dashboard))
    a = int(input("""\n1.activar robot\n2.desactivar robot\n3.Eliminar Alarma
4.Calibrar coordenadas\n5. posicion actual\n6.estado de entradas\n7. Moverpos1\n8.StateRobot
9.Ircoordenadas\n=>"""))

    if(a==1 or a==2):
        ActivarRobot(dashboard, feed)

    elif(a==3):
        EliminarAlarma(dashboard)
    elif(a==4):
        calibracion = True
    elif(a==5):
        pose = dashboard.GetPose()
        
        posicionActual = pose.split(",")
        posicionActual=posicionActual[1:posicionActual.index('GetPose();')]
        posicionActual[0]= posicionActual[0].replace("{","")
        posicionActual[-1]= posicionActual[-1].replace("}","")
        print("\n\nposicionActual" ,posicionActual)
        if(calibracion == True):
            print("calibracion iniciada")
            for pos in range(len(posicionActual)):
                posis[pos] = float(posicionActual[pos])
            print(posis)
            time.sleep(1)
            calibracion= False
            pointMemory = posis.copy()
        #print(posicionActual)
    elif(a==6):
        #16 inpus
        inpu = int(input("entrada que desea consultar(1-16): "))
        if(inpu>=1 and inpu<=16):
            #ERROR - STATE -ENTRADA
            print(dashboard.DI(inpu))
        else:
            print("el numero debe estar entre 1-16")
    elif a==7:
        #pos =input("posiciones").split(",")
        move.RelMovJ(10,10,10,0,0,0)

    elif a==8:
        #4 deshabilitado
        #5 habilitado
        #9 error
        State = dashboard.RobotMode().split(",")
        print(State[1])
    elif a==9:
        for x in range(10):
            dashboard.SpeedFactor(10)
            dashboard.DO(1,0)
            dashboard.DO(2,0)
            posiAux = [posis[0],posis[1],posis[2],posis[3],posis[4],posis[5]]
            move.MovL(posis[0],posis[1],posis[2],posis[3],posis[4],posis[5])
            wait_arrive(posiAux)
            print("Llwfo  L |1")
            
