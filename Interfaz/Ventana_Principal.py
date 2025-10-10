import sys, os, cv2
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap

# Asegurar que podamos importar módulos del proyecto si fuera necesario
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reconocimiento Facial - Cámara Integrada")
        self.setGeometry(100, 100, 800, 600)

        # ---- Interfaz ----
        self.label_video = QLabel(self)
        self.label_video.setFixedSize(640, 480)
        self.label_video.setAlignment(Qt.AlignCenter)
        self.label_video.setStyleSheet("background-color: #000; border-radius: 8px;")

        self.boton_iniciar = QPushButton("Iniciar Cámara")
        self.boton_detener = QPushButton("Detener Cámara")
        self.boton_detener.setEnabled(False)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label_video, alignment=Qt.AlignCenter)
        layout.addWidget(self.boton_iniciar, alignment=Qt.AlignCenter)
        layout.addWidget(self.boton_detener, alignment=Qt.AlignCenter)

        contenedor = QWidget()
        contenedor.setLayout(layout)
        self.setCentralWidget(contenedor)

        # ---- Cámara ----
        self.camara = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_frame)

        # ---- Eventos ----
        self.boton_iniciar.clicked.connect(self.iniciar_camara)
        self.boton_detener.clicked.connect(self.detener_camara)

    # ---- Funciones ----
    def iniciar_camara(self):
        self.camara = cv2.VideoCapture(0)
        if not self.camara.isOpened():
            self.label_video.setText("❌ No se pudo acceder a la cámara")
            return

        self.boton_iniciar.setEnabled(False)
        self.boton_detener.setEnabled(True)
        self.timer.start(30)  # actualiza cada 30 ms (~33 FPS)

    def actualizar_frame(self):
        ret, frame = self.camara.read()
        if not ret:
            return

        # Convertir BGR (OpenCV) a RGB (Qt)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_por_linea = ch * w
        imagen_qt = QImage(frame.data, w, h, bytes_por_linea, QImage.Format_RGB888)

        # Mostrar imagen en el QLabel
        self.label_video.setPixmap(QPixmap.fromImage(imagen_qt))

    def detener_camara(self):
        if self.camara:
            self.timer.stop()
            self.camara.release()
            self.label_video.clear()
            self.label_video.setText("Cámara detenida")

        self.boton_iniciar.setEnabled(True)
        self.boton_detener.setEnabled(False)

    def closeEvent(self, event):
        """Cerrar correctamente la cámara al salir."""
        self.detener_camara()
        event.accept()


# ---- Punto de entrada ----
def main():
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
