import cv2

class Camara:
    def __init__(self, index=0):
        self.index = index
        self.captura = None

    def iniciar(self):
        """Inicia la captura de video"""
        self.captura = cv2.VideoCapture(self.index)
        return self.captura.isOpened()

    def obtener_frame(self):
        """Obtiene un frame de la cámara"""
        if self.captura and self.captura.isOpened():
            ret, frame = self.captura.read()
            return frame if ret else None
        return None

    def detener(self):
        """Detiene la captura de video"""
        if self.captura:
            self.captura.release()
            self.captura = None