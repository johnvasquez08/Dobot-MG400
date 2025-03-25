import cv2
import numpy as np

# Datos de calibración directamente en el código
matriz_camara = np.array([
    [1455.5428673773379, 0.0, 980.4199586143592],
    [0.0, 1457.3455869579307, 546.1515511461722],
    [0.0, 0.0, 1.0]
], dtype=np.float32)

coef_distorcion = np.array([
    [0.13735963148970454, -0.7799725541645359, 0.0020087290833629623, 
     -0.00029266933856838997, 1.0552829276882483]
], dtype=np.float32)

# Relación de 50 mm por 166 px
relacion_pixel_mm = 50/163

# URL de la cámara IP (ajusta la dirección IP según tu configuración)
url = "http://192.168.80.78:8080/video"  # Usa la IP de tu teléfono

# Nombre de la ventana
nombre_ventana = "Detección de Círculos con Mediciones (mm) - Corrección de Distorsión"

# Crear ventana con flag para permitir redimensionamiento
cv2.namedWindow(nombre_ventana, cv2.WINDOW_NORMAL)

# Conectar a la cámara
cap = cv2.VideoCapture(url)

# Comprobar si la conexión fue exitosa
if not cap.isOpened():
    print("Error al abrir la cámara")
    exit()

print("Mostrando video con detección de círculos y mediciones.")
print("- Imagen corregida usando parámetros de calibración")
print("- El punto rojo indica el centro de la imagen")
print("- Los círculos detectados se marcan en verde")
print("- Las líneas muestran la distancia horizontal y vertical")
print("- Presiona 'q' para salir")

# Variables para almacenar mapas de corrección de distorsión
mapx = None
mapy = None

while True:
    # Leer un frame
    ret, frame = cap.read()
    
    if not ret:
        print("Error al leer el frame")
        break
    
    # Obtener dimensiones del frame
    height, width = frame.shape[:2]
    
    # Crear mapas de corrección de distorsión si aún no existen
    if mapx is None or mapy is None:
        # Obtener nuevas matrices de cámara para imágenes sin distorsión
        new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(
            matriz_camara, coef_distorcion, (width, height), 1, (width, height))
        
        # Calcular mapas de corrección de distorsión
        mapx, mapy = cv2.initUndistortRectifyMap(
            matriz_camara, coef_distorcion, None, new_camera_matrix, (width, height), cv2.CV_32FC1)
    
    # Aplicar corrección de distorsión
    undistorted = cv2.remap(frame, mapx, mapy, cv2.INTER_LINEAR)
    
    # Usar la imagen sin distorsión para el procesamiento
    frame = undistorted
    
    # Obtener dimensiones del frame (podrían haber cambiado después de la corrección)
    height, width = frame.shape[:2]
    center_x, center_y = width // 2, height // 2
    
    # Crear una copia del frame para dibujar
    output = frame.copy()
    
    # Mostrar las dimensiones de la imagen en la esquina superior izquierda
    dimensions_text = f"Dimensiones: {width}x{height} px"
    cv2.putText(output, dimensions_text, (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Dibujar un círculo rojo en el centro de la imagen
    cv2.circle(output, (center_x, center_y), 10, (0, 0, 255), -1)
    cv2.putText(output, "(0,0) mm", (center_x + 15, center_y), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    # Convertir a escala de grises para la detección de círculos
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Aplicar un desenfoque para reducir el ruido
    gray = cv2.GaussianBlur(gray, (9, 9), 2)
    
    # Detectar círculos usando HoughCircles
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
                              param1=100, param2=30, minRadius=10, maxRadius=100)
    
    # Verificar si se encontraron círculos
    if circles is not None:
        # Convertir las coordenadas y radio a enteros
        circles = np.int32(np.around(circles))
        
        for circle in circles[0, :]:
            # Obtener las coordenadas del centro y el radio
            x, y, r = circle
            
            # Calcular la distancia desde el centro de la imagen en píxeles
            dist_x_px = x - center_x
            dist_y_px = center_y - y  # Y invertido (positivo hacia arriba)
            
            # Convertir las distancias a milímetros
            dist_x_mm = round(dist_x_px * relacion_pixel_mm, 1)
            dist_y_mm = round(dist_y_px * relacion_pixel_mm, 1)
            
            # Dibujar el círculo detectado
            cv2.circle(output, (x, y), r, (0, 255, 0), 2)
            # Dibujar un pequeño círculo en el centro
            cv2.circle(output, (x, y), 2, (0, 255, 0), 3)
            
            # Dibujar líneas horizontales y verticales desde el centro de la imagen al centro del círculo
            # Línea horizontal (componente X)
            cv2.line(output, (center_x, y), (x, y), (0, 255, 255), 2)
            # Línea vertical (componente Y)
            cv2.line(output, (x, center_y), (x, y), (0, 255, 255), 2)
            
            # Mostrar las coordenadas relativas al centro en milímetros
            coord_text = f"({dist_x_mm},{dist_y_mm}) mm"
            cv2.putText(output, coord_text, (x + 10, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Mostrar la distancia en X en milímetros
            x_dist_text = f"X: {dist_x_mm} mm"
            x_text_pos_y = y + 20 if y < height - 30 else y - 20  # Evitar texto fuera de la imagen
            cv2.putText(output, x_dist_text, (center_x + dist_x_px//2, x_text_pos_y), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            # Mostrar la distancia en Y en milímetros
            y_dist_text = f"Y: {dist_y_mm} mm"
            y_text_pos_x = x + 10 if x < width - 100 else x - 100  # Evitar texto fuera de la imagen
            cv2.putText(output, y_dist_text, (y_text_pos_x, center_y + dist_y_px//2), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            # Imprimir valores para depuración
            print(f"Centro de imagen: ({center_x}, {center_y}), Centro de círculo: ({x}, {y}), Distancia en mm: ({dist_x_mm}, {dist_y_mm})")
    
    # Mostrar el frame con las detecciones
    cv2.imshow(nombre_ventana, output)
    
    # Salir si se presiona la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar recursos
cap.release()
cv2.destroyAllWindows()
