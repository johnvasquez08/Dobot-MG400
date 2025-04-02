import cv2
import numpy as np
import os
import json
from datetime import datetime

class CameraCalibrator:
    def __init__(self):
        # Configuración de carpetas
        self.calibration_folder = "C:/Users/johnd/Downloads/Dobot MG400-20250325T192116Z-001/Dobot MG400/calibration_images"
        self.undistorted_folder = "C:/Users/johnd/Downloads/Dobot MG400-20250325T192116Z-001/Dobot MG400/undistorted_images"
        
        # Crear carpetas si no existen
        os.makedirs(self.calibration_folder, exist_ok=True)
        os.makedirs(self.undistorted_folder, exist_ok=True)
        
        # Contador de imágenes capturadas
        self.image_count = 0
        
        # Parámetros del tablero de ajedrez (ajustar según tu tablero)
        self.chessboard_size = (5, 7)  # Número de esquinas internas
        
        # Preparar puntos objeto (0,0,0), (1,0,0), (2,0,0), ...
        self.objp = np.zeros((self.chessboard_size[0] * self.chessboard_size[1], 3), np.float32)
        self.objp[:, :2] = np.mgrid[0:self.chessboard_size[0], 0:self.chessboard_size[1]].T.reshape(-1, 2)
        
        # Arrays para almacenar puntos de objetos y puntos de imagen
        self.objpoints = []  # Puntos 3D en el espacio real
        self.imgpoints = []  # Puntos 2D en el plano de la imagen
        
        # Ventana redimensionable
        self.window_name = "Camera Calibration"
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
    
    def start_capture(self):
        cap = cv2.VideoCapture(3)
        
        
        if not cap.isOpened():
            print("Error: No se pudo abrir la cámara.")
            return
        
        print("Instrucciones:")
        print("- Presiona 'f' para capturar una imagen")
        print("- Presiona 'x' para realizar la calibración")
        print("- Presiona 'q' para salir")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: No se pudo capturar el frame.")
                break
            
            frame = cv2.resize(frame, (640, 640))  # Redimensionar a 640x640
            
            text = f"Imágenes capturadas: {self.image_count}"
            cv2.putText(frame, text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            cv2.imshow(self.window_name, frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('f'):
                self.capture_image(frame)
            elif key == ord('x'):
                cap.release()
                self.calibrate_camera()
                break
            elif key == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
    
    def capture_image(self, frame):
        # Guardar imagen
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.calibration_folder}/calibration_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        
        # Incrementar contador
        self.image_count += 1
        print(f"Imagen guardada: {filename}")
        
        # Buscar esquinas del tablero para verificar
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, self.chessboard_size, None)
        
        if ret:
            print("Tablero de ajedrez detectado correctamente")
        else:
            print("¡Advertencia! No se detectó el tablero de ajedrez en esta imagen")
    
    def calibrate_camera(self):
        print("\nIniciando calibración de la cámara...")
        
        if self.image_count == 0:
            print("Error: No hay imágenes para calibrar.")
            return
        
        # Procesar todas las imágenes en la carpeta de calibración
        image_files = [os.path.join(self.calibration_folder, f) for f in os.listdir(self.calibration_folder) 
                      if f.startswith('calibration_') and f.endswith('.jpg')]
        
        if not image_files:
            print("Error: No se encontraron imágenes de calibración.")
            return
        
        print(f"Procesando {len(image_files)} imágenes para calibración...")
        
        # Criterios de terminación para la detección de esquinas
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        
        for img_file in image_files:
            img = cv2.imread(img_file)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Encontrar esquinas del tablero
            ret, corners = cv2.findChessboardCorners(gray, self.chessboard_size, None)
            
            if ret:
                self.objpoints.append(self.objp)
                
                # Refinar las esquinas a nivel de subpíxel
                corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                self.imgpoints.append(corners2)
                
                # Dibujar y mostrar las esquinas
                cv2.drawChessboardCorners(img, self.chessboard_size, corners2, ret)
                
                # Guardar imagen con esquinas marcadas
                base_name = os.path.basename(img_file)
                marked_file = os.path.join(self.calibration_folder, "marked_" + base_name)
                cv2.imwrite(marked_file, img)
            else:
                print(f"No se pudo encontrar el tablero en la imagen: {img_file}")
        
        if not self.objpoints:
            print("Error: No se pudo detectar el tablero en ninguna imagen.")
            return
        
        print("Calculando parámetros de calibración...")
        
        # Calibrar la cámara
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
            self.objpoints, self.imgpoints, gray.shape[::-1], None, None
        )
        
        if not ret:
            print("Error en la calibración de la cámara.")
            return
        
        print("\nCalibración completada con éxito!")
        print("\nMatriz de la cámara:")
        print(mtx)
        print("\nCoeficientes de distorsión:")
        print(dist)
        
        # Guardar parámetros en un archivo JSON
        calibration_data = {
            "camera_matrix": mtx.tolist(),
            "distortion_coefficients": dist.tolist()
        }
        
        with open("camera_calibration.json", "w") as f:
            json.dump(calibration_data, f, indent=4)
        
        print("\nParámetros de calibración guardados en 'camera_calibration.json'")
        
        # Remover distorsión de las imágenes
        self.undistort_images(mtx, dist)
    
    def undistort_images(self, camera_matrix, dist_coeffs):
        print("\nRemoviendo distorsión de las imágenes...")
        
        image_files = [os.path.join(self.calibration_folder, f) for f in os.listdir(self.calibration_folder) 
                      if f.startswith('calibration_') and f.endswith('.jpg')]
        
        for img_file in image_files:
            img = cv2.imread(img_file)
            h, w = img.shape[:2]
            
            # Obtener nueva matriz de cámara optimizada
            newcameramtx, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coeffs, (w, h), 1, (w, h))
            
            # Remover distorsión
            dst = cv2.undistort(img, camera_matrix, dist_coeffs, None, newcameramtx)
            
            # Recortar la región de interés
            x, y, w, h = roi
            if all(v > 0 for v in [x, y, w, h]):
                dst = dst[y:y+h, x:x+w]
            
            # Guardar imagen sin distorsión
            base_name = os.path.basename(img_file)
            undistorted_file = os.path.join(self.undistorted_folder, "undistorted_" + base_name)
            cv2.imwrite(undistorted_file, dst)
        
        print(f"Se han guardado {len(image_files)} imágenes sin distorsión en la carpeta '{self.undistorted_folder}'")


if __name__ == "__main__":
    calibrator = CameraCalibrator()
    calibrator.start_capture()