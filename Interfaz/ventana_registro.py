import os
import sys
import json
import cv2
import numpy as np

from PySide6.QtWidgets import (
    QMainWindow, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QWidget, QMessageBox
)
from PySide6 import QtCore, QtGui, QtUiTools
from PySide6.QtCore import QTimer, Qt

# === RUTAS RELATIVAS AL PROYECTO ===
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATOS_DIR = os.path.join(PROJECT_ROOT, "Datos")
ROSTROS_DIR = os.path.join(DATOS_DIR, "rostros")
EMBEDDINGS_DIR = os.path.join(DATOS_DIR, "embeddings")
USUARIOS_JSON = os.path.join(DATOS_DIR, "usuarios.json")
UI_PATH = os.path.join(os.path.dirname(__file__), "Registro_Alumno_o.ui")

os.makedirs(DATOS_DIR, exist_ok=True)
os.makedirs(ROSTROS_DIR, exist_ok=True)
os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

# === IMPORTAR CAMARA Y RECONOCIMIENTO ===
try:
    from Nucleo.Camara import Camara
    from Nucleo.Reconocimiento import ReconocimientoFacial
except Exception:
    sys.path.append(os.path.join(PROJECT_ROOT, "Nucleo"))
    from Camara import Camara
    from Reconocimiento import ReconocimientoFacial


class VentanaRegistro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Registro de Usuario")
        self.setGeometry(400, 200, 500, 600)

        # --- Cargar UI ---
        if os.path.exists(UI_PATH):
            loader = QtUiTools.QUiLoader()
            ui_file = QtCore.QFile(UI_PATH)
            ui_file.open(QtCore.QFile.ReadOnly)
            self.ui = loader.load(ui_file, self)
            ui_file.close()
            self.setCentralWidget(self.ui)
        else:
            self._build_ui_fallback()

        # --- Instancias ---
        self.camara = Camara()
        self.recon = ReconocimientoFacial()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_preview)
        self.ruta_rostro = None

        # --- Mapeo widgets ---
        self._map_widgets()
        self._conectar_eventos()

        # --- Iniciar cámara automáticamente ---
        QtCore.QTimer.singleShot(300, self.iniciar_camara)

    def _build_ui_fallback(self):
        """Interfaz mínima si no existe UI"""
        central = QWidget()
        layout = QVBoxLayout(central)

        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre completo")

        self.input_usuario = QLineEdit()
        self.input_usuario.setPlaceholderText("Usuario")

        self.input_contrasena = QLineEdit()
        self.input_contrasena.setPlaceholderText("Contraseña")
        self.input_contrasena.setEchoMode(QLineEdit.Password)

        self.label_preview = QLabel()
        self.label_preview.setFixedSize(320, 240)
        self.label_preview.setStyleSheet("background:#111; color:#aaa;")
        self.label_preview.setAlignment(Qt.AlignCenter)

        self.btn_capturar = QPushButton("Capturar rostro")
        self.btn_guardar = QPushButton("Guardar usuario")

        layout.addWidget(self.input_nombre)
        layout.addWidget(self.input_usuario)
        layout.addWidget(self.input_contrasena)
        layout.addWidget(self.label_preview)
        layout.addWidget(self.btn_capturar)
        layout.addWidget(self.btn_guardar)

        self.setCentralWidget(central)

    def _map_widgets(self):
        """Asigna widgets tanto para UI cargada como fallback"""
        def g(name):
            try:
                return self.ui.findChild(QtCore.QObject, name)
            except Exception:
                return None

        if hasattr(self, "ui"):
            self.input_nombre = g("input_nombre") or g("lineEdit_nombre") or self.input_nombre
            self.input_usuario = g("input_usuario") or g("lineEdit_usuario") or self.input_usuario
            self.input_contrasena = g("input_contrasena") or g("lineEdit_contrasena") or self.input_contrasena
            self.label_preview = g("label_preview") or g("label_video") or self.label_preview
            self.btn_capturar = g("btn_capturar") or g("pushButton_capturar") or self.btn_capturar
            self.btn_guardar = g("btn_guardar") or g("pushButton_guardar") or self.btn_guardar

    def _conectar_eventos(self):
        self.btn_capturar.clicked.connect(self.capturar_rostro)
        self.btn_guardar.clicked.connect(self.guardar_usuario)

    def iniciar_camara(self):
        """Inicia la cámara y el timer de preview"""
        if self.camara.iniciar():
            self.timer.start(30)
        else:
            QMessageBox.warning(self, "Error", "No se pudo iniciar la cámara.")

    def actualizar_preview(self):
        frame = self.camara.obtener_frame()
        if frame is None:
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.recon.detector.detectMultiScale(gray, 1.1, 5, minSize=(80, 80))
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        image = QtGui.QImage(rgb.data, w, h, ch * w, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(image).scaled(self.label_preview.width(), self.label_preview.height(), Qt.KeepAspectRatio)
        self.label_preview.setPixmap(pixmap)

    def capturar_rostro(self):
        frame = self.camara.obtener_frame()
        if frame is None:
            QMessageBox.warning(self, "Error", "No se obtuvo imagen de la cámara.")
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.recon.detector.detectMultiScale(gray, 1.1, 5, minSize=(80, 80))
        if len(faces) == 0:
            QMessageBox.warning(self, "Sin rostro", "No se detectó ningún rostro.")
            return

        x, y, w, h = faces[0]
        rostro = frame[y:y + h, x:x + w]
        usuario = self.input_usuario.text().strip()
        if not usuario:
            QMessageBox.warning(self, "Error", "Debes ingresar un nombre de usuario antes de capturar.")
            return

        ruta = os.path.join(ROSTROS_DIR, f"{usuario}.jpg")
        cv2.imwrite(ruta, rostro)
        self.ruta_rostro = ruta

        QMessageBox.information(self, "Captura", "✅ Rostro guardado correctamente.")

    def guardar_usuario(self):
        nombre = self.input_nombre.text().strip()
        usuario = self.input_usuario.text().strip()
        contrasena = self.input_contrasena.text().strip()

        if not all([nombre, usuario, contrasena, self.ruta_rostro]):
            QMessageBox.warning(self, "Error", "Completa todos los campos y captura el rostro.")
            return

        # Cargar usuarios existentes
        if os.path.exists(USUARIOS_JSON):
            with open(USUARIOS_JSON, "r", encoding="utf-8") as f:
                try:
                    datos = json.load(f)
                except:
                    datos = []
        else:
            datos = []

        # Validar duplicados
        for u in datos:
            if u.get("usuario") == usuario:
                QMessageBox.warning(self, "Error", "El usuario ya existe.")
                return

        nuevo = {
            "nombre": nombre,
            "usuario": usuario,
            "contrasena": contrasena,
            "rostro": os.path.relpath(self.ruta_rostro, PROJECT_ROOT)
        }
        datos.append(nuevo)

        with open(USUARIOS_JSON, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)

        # Extraer embedding y guardarlo en carpeta embeddings
        try:
            from deepface import DeepFace
            rep = DeepFace.represent(self.ruta_rostro, model_name=self.recon.modelo, enforce_detection=True)
            if isinstance(rep, list) and len(rep) > 0:
                emb = np.array(rep[0]["embedding"], dtype=np.float32)

                # Archivo donde guardaremos todos los embeddings y nombres
                emb_path = os.path.join(EMBEDDINGS_DIR, "embeddings.npy")
                names_path = os.path.join(EMBEDDINGS_DIR, "nombres.json")

                # Cargar existentes si hay
                if os.path.exists(emb_path):
                    existing_embs = np.load(emb_path)
                else:
                    existing_embs = np.empty((0, len(emb)), dtype=np.float32)

                # Concatenar nuevo embedding
                new_embs = np.vstack([existing_embs, emb])

                # Guardar embeddings actualizados
                np.save(emb_path, new_embs)

                # Guardar nombres asociados
                if os.path.exists(names_path):
                    with open(names_path, "r", encoding="utf-8") as f:
                        names = json.load(f)
                else:
                    names = []

                names.append(nombre)
                with open(names_path, "w", encoding="utf-8") as f:
                    json.dump(names, f, indent=4, ensure_ascii=False)

        except Exception as e:
            print(f"⚠️ No se pudo extraer o guardar embedding: {e}")

        QMessageBox.information(self, "Registro exitoso", "✅ Usuario registrado correctamente.")
        self.close()

    def closeEvent(self, ev):
        self.timer.stop()
        self.camara.detener()
        ev.accept()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    ventana = VentanaRegistro()
    ventana.show()
    sys.exit(app.exec())
