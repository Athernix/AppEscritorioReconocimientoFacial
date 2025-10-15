# Camara.py
import cv2

class Camara:
    def __init__(self, index=0):
        self.index = index
        self.captura = None

    def iniciar(self):
        """Inicia la captura con configuración optimizada"""
        self.captura = cv2.VideoCapture(self.index)
        if self.captura.isOpened():
            # Configuración para máximo rendimiento
            self.captura.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.captura.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.captura.set(cv2.CAP_PROP_FPS, 20)
            self.captura.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reducir buffer
            return True
        return False

    def obtener_frame(self):
        """Obtiene frame optimizado"""
        if self.captura and self.captura.isOpened():
            ret, frame = self.captura.read()
            return frame if ret else None
        return None

    def detener(self):
        """Detiene la captura"""
        if self.captura:
            self.captura.release()
            self.captura = None