import cv2
import numpy as np
import math

# Variables globales para el manejo de eventos del mouse
drawing = False
start_point = (-1, -1)
end_point = (-1, -1)

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
    global start_point, end_point
    
    # Solicitar la URL del video al usuario
    url = "http://192.168.80.78:8080/video"
    cap = cv2.VideoCapture(3)
    
    # Verificar si se abrió correctamente
    if not cap.isOpened():
        print("Error al abrir el video")
        return
    
    # Crear una ventana redimensionable y asignar el callback del mouse
    window_name = "Video - Dibuja una línea para medir (ESC para salir, R para reiniciar)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)  # WINDOW_NORMAL permite redimensionar
    cv2.setMouseCallback(window_name, mouse_callback)
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Error al leer el frame")
            break
        
        # Crear una copia del frame para dibujar
        display_frame = frame.copy()
        
        # Dibujar la línea si hay puntos válidos
        if start_point[0] != -1 and end_point[0] != -1:
            cv2.line(display_frame, start_point, end_point, (0, 255, 0), 2)
            
            # Calcular la longitud de la línea
            length = math.sqrt((end_point[0] - start_point[0])**2 + 
                              (end_point[1] - start_point[1])**2)
            
            # Mostrar la longitud en la imagen
            text = f"Longitud: {length:.2f} pixeles"
            cv2.putText(display_frame, text, (30, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
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
