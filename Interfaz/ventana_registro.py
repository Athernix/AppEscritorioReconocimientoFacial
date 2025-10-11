import cv2
import json
import os
from PySide6.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class VentanaRegistro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Registro de Usuario")
        self.setGeometry(300, 200, 400, 400)
        self.setStyleSheet("background-color: #0d0d0d; color: white;")

        # --- Título ---
        self.titulo = QLabel("Registrar nuevo usuario")
        self.titulo.setAlignment(Qt.AlignCenter)
        self.titulo.setFont(QFont("Arial", 14, QFont.Bold))
        self.titulo.setStyleSheet("color: #00bfff; margin-bottom: 10px;")

        # --- Entradas ---
        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre completo")
        self.input_usuario = QLineEdit()
        self.input_usuario.setPlaceholderText("Usuario")
        self.input_contrasena = QLineEdit()
        self.input_contrasena.setPlaceholderText("Contraseña")
        self.input_contrasena.setEchoMode(QLineEdit.Password)

        for campo in [self.input_nombre, self.input_usuario, self.input_contrasena]:
            campo.setStyleSheet("""
                background-color: #1f1f1f; border: none; border-radius: 6px;
                padding: 8px; color: white;
            """)

        # --- Botones ---
        self.btn_capturar = QPushButton("Capturar Rostro")
        self.btn_guardar = QPushButton("Guardar Registro")

        for b in [self.btn_capturar, self.btn_guardar]:
            b.setStyleSheet("""
                QPushButton {
                    background-color: #333;
                    color: white;
                    border-radius: 6px;
                    padding: 8px 12px;
                }
                QPushButton:hover {
                    background-color: #555;
                }
            """)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.titulo)
        layout.addWidget(self.input_nombre)
        layout.addWidget(self.input_usuario)
        layout.addWidget(self.input_contrasena)
        layout.addWidget(self.btn_capturar)
        layout.addWidget(self.btn_guardar)
        layout.addStretch()

        contenedor = QWidget()
        contenedor.setLayout(layout)
        self.setCentralWidget(contenedor)

        # --- Eventos ---
        self.btn_capturar.clicked.connect(self.capturar_rostro)
        self.btn_guardar.clicked.connect(self.guardar_usuario)

        self.ruta_rostro = None

    def capturar_rostro(self):
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            QMessageBox.warning(self, "Error", "No se pudo acceder a la cámara.")
            return

        detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        QMessageBox.information(self, "Instrucción", "Presiona 's' para guardar el rostro o 'q' para cancelar.")

        rostro_guardado = None
        while True:
            ret, frame = cam.read()
            if not ret:
                break

            gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rostros = detector.detectMultiScale(gris, 1.3, 5)

            for (x, y, w, h) in rostros:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                rostro_guardado = frame[y:y+h, x:x+w]

            cv2.imshow("Captura de Rostro", frame)
            tecla = cv2.waitKey(1)
            if tecla == ord('s') and rostro_guardado is not None:
                usuario = self.input_usuario.text().strip()
                if not usuario:
                    QMessageBox.warning(self, "Error", "Debes ingresar un usuario antes de capturar.")
                    break
                ruta = f"Datos/rostros/{usuario}.png"
                cv2.imwrite(ruta, rostro_guardado)
                self.ruta_rostro = ruta
                QMessageBox.information(self, "Éxito", f"Rostro guardado como: {ruta}")
                break
            elif tecla == ord('q'):
                break

        cam.release()
        cv2.destroyAllWindows()

    def guardar_usuario(self):
        nombre = self.input_nombre.text().strip()
        usuario = self.input_usuario.text().strip()
        contrasena = self.input_contrasena.text().strip()

        if not all([nombre, usuario, contrasena, self.ruta_rostro]):
            QMessageBox.warning(self, "Error", "Completa todos los campos y captura el rostro.")
            return

        nuevo = {
            "nombre": nombre,
            "usuario": usuario,
            "contrasena": contrasena,
            "rostro": self.ruta_rostro
        }

        ruta_json = "Datos/usuarios.json"
        if os.path.exists(ruta_json):
            with open(ruta_json, "r", encoding="utf-8") as f:
                datos = json.load(f)
        else:
            datos = []

        datos.append(nuevo)

        with open(ruta_json, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)

        QMessageBox.information(self, "Registro", "Usuario registrado correctamente.")
        self.close()
