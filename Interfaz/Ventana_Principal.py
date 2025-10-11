import cv2
import json
import os
import numpy as np
from PySide6.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QWidget, QGridLayout, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap, QFont

from Nucleo.Reconocimiento import ReconocimientoFacial
from Nucleo.Camara import Camara


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reconocimiento Facial - Principal")
        self.setGeometry(200, 100, 900, 600)
        self.setStyleSheet("background-color: #0d0d0d; color: white;")

        # ---------- Instancias de módulos ----------
        self.reconocimiento = ReconocimientoFacial()
        self.camara = Camara()
        
        # ---------- UI ----------
        self.setup_ui()
        
        # ---------- Sistema de reconocimiento ----------
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_frame)
        self.boton_detener.setEnabled(False)

        # Inicializar el reconocedor
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        # ---------- Eventos ----------
        self.boton_iniciar.clicked.connect(self.iniciar_camara)
        self.boton_detener.clicked.connect(self.detener_camara)
        self.boton_registro.clicked.connect(self.registrar_usuario)

        # ---------- Variables para el reconocimiento ----------
        self.rostros_entrenados = []
        self.labels = []
        self.nombres_dict = {}
        
        # Cargar rostros conocidos
        self.cargar_rostros()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # ---------- Encabezado ----------
        self.label_logo = QLabel("SISTEMA DE RECONOCIMIENTO FACIAL")
        self.label_logo.setAlignment(Qt.AlignCenter)
        self.label_logo.setFixedHeight(60)
        self.label_logo.setStyleSheet("""
            background-color: #1a1a1a;
            color: #00bfff;
            font-weight: bold;
            font-size: 18px;
            border-radius: 8px;
        """)

        # ---------- Video ----------
        self.label_video = QLabel()
        self.label_video.setFixedSize(300, 300)
        self.label_video.setAlignment(Qt.AlignCenter)
        self.label_video.setStyleSheet("""
            background-color: #1a1a1a;
            border-radius: 12px;
        """)

        # ---------- Información del rostro detectado ----------
        self.label_nombres = QLabel("USUARIO DETECTADO")
        self.label_nombres.setFont(QFont("Arial", 10, QFont.Bold))
        self.label_nombres.setStyleSheet("color: gray;")

        self.nombre_detectado = QLabel("Desconocido")
        self.nombre_detectado.setStyleSheet("background-color: #1f1f1f; border-radius: 4px; padding: 8px;")

        # Layout nombres
        nombres_layout = QVBoxLayout()
        nombres_layout.addWidget(self.label_nombres)
        nombres_layout.addWidget(self.nombre_detectado)

        # ---------- Roles y acceso ----------
        roles_layout = QGridLayout()
        roles_layout.setHorizontalSpacing(20)
        roles_layout.addWidget(QLabel("ROL"), 0, 0)
        roles_layout.addWidget(QLabel("ACCESO"), 0, 1)

        self.lbl_rol = QLabel("VISITANTE")
        self.lbl_estado = QLabel("DENEGADO")
        self.lbl_rol.setStyleSheet("background-color: #1f1f1f; border-radius: 4px; padding: 6px;")
        self.lbl_estado.setStyleSheet("background-color: #1f1f1f; border-radius: 4px; padding: 6px; color: red;")

        roles_layout.addWidget(self.lbl_rol, 1, 0)
        roles_layout.addWidget(self.lbl_estado, 1, 1)

        # ---------- Botones ----------
        self.boton_iniciar = QPushButton("Iniciar Cámara")
        self.boton_detener = QPushButton("Detener Cámara")
        self.boton_registro = QPushButton("Registrar Nuevo Usuario")
        for boton in [self.boton_iniciar, self.boton_detener, self.boton_registro]:
            boton.setStyleSheet("""
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

        botones_layout = QHBoxLayout()
        botones_layout.addWidget(self.boton_iniciar)
        botones_layout.addWidget(self.boton_detener)
        botones_layout.addWidget(self.boton_registro)

        # ---------- Layout principal ----------
        parte_central = QHBoxLayout()
        parte_central.addLayout(nombres_layout)
        parte_central.addWidget(self.label_video, alignment=Qt.AlignCenter)
        parte_central.addLayout(roles_layout)

        contenedor = QWidget()
        layout_principal = QVBoxLayout(contenedor)
        layout_principal.addWidget(self.label_logo)
        layout_principal.addSpacing(20)
        layout_principal.addLayout(parte_central)
        layout_principal.addSpacing(20)
        layout_principal.addLayout(botones_layout)

        self.setCentralWidget(contenedor)

    def cargar_rostros(self):
        """Carga todos los rostros conocidos y entrena el modelo"""
        print("=" * 50)
        print("🔄 INICIANDO CARGA DE ROSTROS...")
        
        ruta_json = "Datos/usuarios.json"
        if not os.path.exists(ruta_json):
            print("❌ No existe el archivo de usuarios")
            os.makedirs("Datos", exist_ok=True)
            with open(ruta_json, "w", encoding="utf-8") as f:
                json.dump([], f)
            return

        with open(ruta_json, "r", encoding="utf-8") as f:
            try:
                usuarios = json.load(f)
                print(f"📁 Usuarios en JSON: {len(usuarios)}")
            except json.JSONDecodeError:
                usuarios = []
                print("❌ Error leyendo el archivo JSON")

        rostros = []
        labels = []
        nombres_dict = {}
        label_id = 0

        for usuario in usuarios:
            ruta_rostro = usuario["rostro"]
            nombre = usuario["nombre"]
            print(f"🔍 Procesando: {nombre} -> {ruta_rostro}")
            
            if os.path.exists(ruta_rostro):
                try:
                    # Cargar imagen
                    imagen = cv2.imread(ruta_rostro)
                    if imagen is not None:
                        print(f"   ✅ Imagen cargada - Tamaño: {imagen.shape}")
                        
                        # Convertir a escala de grises
                        if len(imagen.shape) == 3:
                            gray = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
                        else:
                            gray = imagen
                        
                        # Mejorar contraste
                        gray = cv2.equalizeHist(gray)
                        
                        # Detectar rostros
                        faces = self.reconocimiento.detector.detectMultiScale(
                            gray, 
                            scaleFactor=1.1, 
                            minNeighbors=5, 
                            minSize=(30, 30)
                        )
                        
                        print(f"   🔍 Rostros detectados: {len(faces)}")
                        
                        if len(faces) > 0:
                            for (x, y, w, h) in faces:
                                face_roi = gray[y:y+h, x:x+w]
                                # Redimensionar
                                face_roi = cv2.resize(face_roi, (200, 200))
                                
                                rostros.append(face_roi)
                                labels.append(label_id)
                                nombres_dict[label_id] = nombre
                                label_id += 1
                                print(f"   ✅ Rostro añadido - Label: {label_id-1}")
                                break
                        else:
                            print(f"   ⚠️ No se detectó rostro en la imagen")
                    else:
                        print(f"   ❌ No se pudo cargar la imagen")
                except Exception as e:
                    print(f"   ❌ Error procesando imagen: {e}")
            else:
                print(f"   ❌ Archivo no existe: {ruta_rostro}")

        # Entrenar el modelo si hay rostros
        if rostros:
            self.face_recognizer.train(rostros, np.array(labels))
            self.rostros_entrenados = rostros
            self.labels = labels
            self.nombres_dict = nombres_dict
            print(f"🎯 MODELO ENTRENADO CON {len(rostros)} ROSTROS")
            print(f"📊 Labels: {labels}")
            print(f"📊 Nombres: {nombres_dict}")
        else:
            self.rostros_entrenados = []
            self.labels = []
            self.nombres_dict = {}
            print("⚠️ NO HAY ROSTROS PARA ENTRENAR")
        print("=" * 50)

    def iniciar_camara(self):
        """Inicia la cámara"""
        if self.camara.iniciar():
            self.timer.start(30)
            self.boton_iniciar.setEnabled(False)
            self.boton_detener.setEnabled(True)
            print("📹 CÁMARA INICIADA")
        else:
            self.label_video.setText("❌ No se pudo acceder a la cámara")
            print("❌ ERROR AL INICIAR CÁMARA")

    def actualizar_frame(self):
        """Actualiza el frame de la cámara y realiza reconocimiento facial"""
        frame = self.camara.obtener_frame()
        if frame is None:
            return

        # Convertir a escala de grises
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_eq = cv2.equalizeHist(gray)
        
        # Detectar rostros
        faces = self.reconocimiento.detector.detectMultiScale(
            gray_eq, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(50, 50)
        )

        nombre_detectado = "Desconocido"
        color_acceso = "red"
        rol = "VISITANTE"
        confianza = 0

        for (x, y, w, h) in faces:
            # Extraer y preprocesar rostro
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (200, 200))
            face_roi = cv2.equalizeHist(face_roi)

            # Intentar reconocer si hay modelo entrenado
            if self.rostros_entrenados:
                try:
                    label, confidence = self.face_recognizer.predict(face_roi)
                    confianza = confidence
                    
                    print(f"🔍 Predicción - Label: {label}, Confianza: {confidence:.1f}")
                    
                    # LBPH: valores más bajos = mayor confianza
                    # PRUEBA DIFERENTES UMBRALES AQUÍ:
                    if confidence < 70:  # ← CAMBIA ESTE VALOR SI ES NECESARIO
                        if label in self.nombres_dict:
                            nombre_detectado = self.nombres_dict[label]
                            rol = "USUARIO REGISTRADO"
                            color_acceso = "green"
                            print(f"✅ RECONOCIDO: {nombre_detectado} (Confianza: {confidence:.1f})")
                        else:
                            print(f"⚠️ Label {label} no encontrado en el diccionario")
                    else:
                        print(f"❌ NO RECONOCIDO - Confianza muy alta: {confidence:.1f}")
                        
                except Exception as e:
                    print(f"❌ ERROR EN PREDICCIÓN: {e}")

            # Dibujar en frame
            color = (0, 255, 0) if color_acceso == "green" else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, f"{nombre_detectado} ({confianza:.1f})", 
                       (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # Actualizar UI
        self.nombre_detectado.setText(nombre_detectado)
        self.lbl_rol.setText(rol)
        estado = "PERMITIDO" if color_acceso == "green" else "DENEGADO"
        self.lbl_estado.setText(estado)
        self.lbl_estado.setStyleSheet(f"color: {color_acceso};")

        # Mostrar frame
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.label_video.setPixmap(QPixmap.fromImage(qt_image.scaled(
            self.label_video.width(), self.label_video.height(), Qt.KeepAspectRatio)))

    def detener_camara(self):
        """Detiene la cámara"""
        self.timer.stop()
        self.camara.detener()
        self.label_video.clear()
        self.label_video.setText("Cámara detenida")
        self.boton_iniciar.setEnabled(True)
        self.boton_detener.setEnabled(False)
        print("⏹️ CÁMARA DETENIDA")

    def registrar_usuario(self):
        """Registra un nuevo usuario"""
        self.detener_camara()

        nombre, usuario, contrasena = self.solicitar_datos_usuario()
        if not nombre:
            return

        # Crear directorios si no existen
        os.makedirs("Datos/rostros", exist_ok=True)
        ruta_rostro = f"Datos/rostros/{usuario}.png"

        print(f"📸 INICIANDO CAPTURA PARA: {nombre}")
        resultado = self.reconocimiento.capturar_rostro(ruta_rostro)
        
        if resultado and os.path.exists(ruta_rostro):
            # Verificar que la imagen es válida y contiene un rostro
            img = cv2.imread(ruta_rostro)
            if img is not None:
                # Verificar si contiene un rostro
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
                faces = self.reconocimiento.detector.detectMultiScale(gray, 1.1, 5)
                
                if len(faces) > 0:
                    self.guardar_usuario_json(nombre, usuario, contrasena, ruta_rostro)
                    QMessageBox.information(self, "Éxito", f"Usuario {usuario} registrado correctamente!")
                    
                    # Recargar el modelo con el nuevo usuario
                    print("🔄 RECARGANDO MODELO CON NUEVO USUARIO...")
                    self.cargar_rostros()
                else:
                    QMessageBox.warning(self, "Error", "No se detectó un rostro en la imagen capturada.")
                    if os.path.exists(ruta_rostro):
                        os.remove(ruta_rostro)
            else:
                QMessageBox.warning(self, "Error", "La imagen capturada no es válida")
                if os.path.exists(ruta_rostro):
                    os.remove(ruta_rostro)
        else:
            QMessageBox.warning(self, "Error", "No se pudo capturar el rostro")

    def solicitar_datos_usuario(self):
        """Solicita los datos del usuario mediante diálogos"""
        nombre, ok1 = QInputDialog.getText(self, "Registro", "Nombre completo:")
        if not ok1 or not nombre.strip():
            return None, None, None
        usuario, ok2 = QInputDialog.getText(self, "Registro", "Usuario:")
        if not ok2 or not usuario.strip():
            return None, None, None
        contrasena, ok3 = QInputDialog.getText(self, "Registro", "Contraseña:")
        if not ok3 or not contrasena.strip():
            return None, None, None
        return nombre.strip(), usuario.strip(), contrasena.strip()

    def guardar_usuario_json(self, nombre, usuario, contrasena, ruta_rostro):
        """Guarda el usuario en el archivo JSON"""
        ruta_json = "Datos/usuarios.json"
        
        if os.path.exists(ruta_json):
            with open(ruta_json, "r", encoding="utf-8") as f:
                try:
                    datos = json.load(f)
                except:
                    datos = []
        else:
            datos = []

        # Verificar si el usuario ya existe
        for user in datos:
            if user["usuario"] == usuario:
                QMessageBox.warning(self, "Error", "El usuario ya existe")
                return

        nuevo_usuario = {
            "nombre": nombre,
            "usuario": usuario,
            "contrasena": contrasena,
            "rostro": ruta_rostro
        }
        datos.append(nuevo_usuario)

        with open(ruta_json, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)

        print(f"✅ USUARIO GUARDADO: {usuario}")

    def closeEvent(self, event):
        """Maneja el cierre de la aplicación"""
        self.detener_camara()
        event.accept()