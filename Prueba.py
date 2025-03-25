from dobot_api import DobotApiDashboard, DobotApiMove

# Conectar con el robot
ip = "192.168.1.6"
port = 29999
dashboard = DobotApiDashboard(ip, port)
move = DobotApiMove(ip, 30003)

# Habilitar el robot
dashboard.EnableRobot()

# Definir posiciones (x, y, z, r)
posicion_1 = [250, 0, 50, 0]
posicion_2 = [300, 0, 50, 0]

# Mover a la primera posición
move.MovL(*posicion_1)

# Esperar un poco para observar el movimiento
move.wait(2)

# Mover a la segunda posición
move.MovL(*posicion_2)

# Finalizar
dashboard.DisableRobot()
