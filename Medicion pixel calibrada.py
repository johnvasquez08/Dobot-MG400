import cv2
import numpy as np
import math

# Datos de calibración directamente en el código
camera_matrix = np.array([
    [1455.5428673773379, 0.0, 980.4199586143592],
    [0.0, 1457.3455869579307, 546.1515511461722],
    [0.0, 0.0, 1.0]
], dtype=np.float32)

dist_coeffs = np.array([
    [0.13735963148970454, -0.7799725541645359, 0.0020087290833629623, 
     -0.00029266933856838997, 1.0552829276882483]
], dtype=np.float32)

# Variables globales para el manejo de eventos del mouse
drawing = False
start_point = (-1, -1)
end_point = (-1, -1)

# Variables para almacenar mapas de corrección de distorsión
mapx = None
mapy = None

def mouse_callback(event, x, y, flags, param):
    global drawing, start_point, end_point
    
    if event == cv2.EVENT_LBUTTONDOWN:
        # Comenzar a dibujar
        drawing = True
        start_point = (x, y)
        end_point = (x, y)
    
    elif event == cv2.EVENT_MOUSEMOVE:
        # Actualizar el punto final mientras se mueve el mouse
        if drawing:
            end_point = (x, y)
    
    elif event == cv2.EVENT_LBUTTONUP:
        # Finalizar el dibujo
        drawing = False
        end_point = (x, y)

def main():
    # Declarar que vamos a usar las variables globales
    global start_point, end_point, mapx, mapy
    
    # URL de la cámara
    url = "http://192.168.80.78:8080/video"
    cap = cv2.VideoCapture(url)
    
    # Verificar si se abrió correctamente
    if not cap.isOpened():
        print("Error al abrir el video")
        return
    
    # Crear una ventana redimensionable y asignar el callback del mouse
    window_name = "Video Corregido - Dibuja una línea para medir (ESC para salir, R para reiniciar)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)  # WINDOW_NORMAL permite redimensionar
    cv2.setMouseCallback(window_name, mouse_callback)
    
    print("Instrucciones:")
    print("- Haz clic y arrastra para medir distancias")
    print("- Presiona 'r' para reiniciar la medición")
    print("- Presiona ESC para salir")
    print("- La imagen está siendo corregida usando los parámetros de calibración")
    
    while True:
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
                camera_matrix, dist_coeffs, (width, height), 1, (width, height))
            
            # Calcular mapas de corrección de distorsión
            mapx, mapy = cv2.initUndistortRectifyMap(
                camera_matrix, dist_coeffs, None, new_camera_matrix, (width, height), cv2.CV_32FC1)
        
        # Aplicar corrección de distorsión
        undistorted = cv2.remap(frame, mapx, mapy, cv2.INTER_LINEAR)
        
        # Usar la imagen sin distorsión para el procesamiento
        display_frame = undistorted.copy()
        
        # Dibujar la línea si hay puntos válidos
        if start_point[0] != -1 and end_point[0] != -1:
            cv2.line(display_frame, start_point, end_point, (0, 255, 0), 2)
            
            # Calcular la longitud de la línea en píxeles
            length_px = math.sqrt((end_point[0] - start_point[0])**2 + 
                               (end_point[1] - start_point[1])**2)
            
            # Mostrar la longitud en píxeles
            text_px = f"Longitud: {length_px:.2f} píxeles"
            cv2.putText(display_frame, text_px, (30, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            # Mostrar las coordenadas de los puntos
            start_text = f"Inicio: ({start_point[0]}, {start_point[1]})"
            end_text = f"Fin: ({end_point[0]}, {end_point[1]})"
            cv2.putText(display_frame, start_text, (30, 70), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            cv2.putText(display_frame, end_text, (30, 100), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            
            # Dibujar círculos en los puntos de inicio y fin
            cv2.circle(display_frame, start_point, 5, (255, 0, 0), -1)
            cv2.circle(display_frame, end_point, 5, (0, 0, 255), -1)
        
        # Agregar indicador de que la imagen está corregida
        cv2.putText(display_frame, "Imagen corregida", (width - 250, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Mostrar el frame
        cv2.imshow(window_name, display_frame)
        
        # Controles de teclado
        key = cv2.waitKey(1)
        if key == 27:  # ESC para salir
            break
        elif key == ord('r'):  # R para reiniciar la línea
            start_point = (-1, -1)
            end_point = (-1, -1)
    
    # Liberar recursos
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
