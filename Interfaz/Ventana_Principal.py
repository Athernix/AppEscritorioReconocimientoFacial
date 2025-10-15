# Ventana_Principal.py
import cv2
import json
import os
import numpy as np
import sys
from PySide6.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QWidget, QGridLayout, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap, QFont

from Nucleo.Reconocimiento import ReconocimientoFacial
from Nucleo.Camara import Camara  # asumo que tu Camara tiene métodos iniciar(), obtener_frame(), detener()

# Import de la ventana de registro (robusto)
try:
    from Interfaz.ventana_registro import VentanaRegistro
except Exception:
    try:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        interfaz_path = os.path.join(project_root, "Interfaz")
        if interfaz_path not in sys.path:
            sys.path.insert(0, interfaz_path)
        from ventana_registro import VentanaRegistro
    except Exception:
        VentanaRegistro = None


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reconocimiento Facial - Principal")
        self.setGeometry(200, 100, 900, 600)
        self.setStyleSheet("background-color: #0d0d0d; color: white;")

        # ---------- Instancias de módulos ----------
        self.reconocimiento = ReconocimientoFacial(modelo="Facenet")
        self.camara = Camara()

        # ---------- UI ----------
        self.setup_ui()

        # ---------- Sistema de reconocimiento ----------
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_frame)
        self.boton_detener.setEnabled(False)

        # Variables UI/estado
        self.nombre_detectado = QLabel("Desconocido")  # ya definido en setup_ui; redefinir por si acaso
        # ---------- Datos de usuarios ----------
        self.ruta_json = os.path.join("Datos", "usuarios.json")
        os.makedirs("Datos", exist_ok=True)

        # ---------- Embeddings dir ----------
        self.embeddings_dir = os.path.join("Datos", "embeddings")
        os.makedirs(self.embeddings_dir, exist_ok=True)

        # Cargar vectores/usuarios
        # Primero intento cargar vectores preguardados (Datos/embeddings)
        self.reconocimiento.cargar_vectores()  # mantiene compatibilidad; puede cargar desde su propia ubicación
        # Luego intento cargar desde Datos/embeddings (si recon no lo hizo)
        self.cargar_rostros()

        # ---------- Eventos ----------
        self.boton_iniciar.clicked.connect(self.iniciar_camara)
        self.boton_detener.clicked.connect(self.detener_camara)
        self.boton_registro.clicked.connect(self.registrar_usuario)

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
        """
        Carga embeddings desde Datos/embeddings si existen.
        Si no existen, intenta extraer embeddings desde Datos/usuarios.json usando DeepFace,
        y guarda los embeddings extraídos en Datos/embeddings para futuras ejecuciones.
        """
        print("=" * 50)
        print("🔄 INICIANDO CARGA DE ROSTROS/EMBEDDINGS...")

        emb_path = os.path.join(self.embeddings_dir, "embeddings.npy")
        names_path = os.path.join(self.embeddings_dir, "nombres.json")

        # Si ya cargamos vectores previamente, no hacemos trabajo extra.
        if len(self.reconocimiento.known_face_encodings) > 0:
            print(f"ℹ️ Ya existen {len(self.reconocimiento.known_face_encodings)} embeddings cargados. Omitiendo re-extracción.")
            print("=" * 50)
            return

        # 1) Intentar cargar embeddings guardados
        try:
            if os.path.exists(emb_path) and os.path.exists(names_path):
                print("ℹ️ Cargando embeddings guardados desde Datos/embeddings/ ...")
                embs = np.load(emb_path, allow_pickle=True)
                with open(names_path, "r", encoding="utf-8") as f:
                    names = json.load(f)
                if embs.ndim == 1:
                    embs = np.expand_dims(embs, 0)
                for emb, name in zip(embs, names):
                    try:
                        self.reconocimiento.known_face_encodings.append(np.array(emb, dtype=np.float32))
                        self.reconocimiento.known_face_names.append(name)
                    except Exception:
                        pass
                print(f"✅ Cargados {len(names)} embeddings desde carpeta de embeddings.")
                print("=" * 50)
                return
        except Exception as e:
            print(f"⚠️ Error cargando embeddings guardados: {e}")

        # 2) Si no hay embeddings guardados, intentar procesar usuarios.json (compatibilidad backward)
        if not os.path.exists(self.ruta_json):
            print("❌ No existe el archivo de usuarios; se crea vacío.")
            with open(self.ruta_json, "w", encoding="utf-8") as f:
                json.dump([], f)
            print("=" * 50)
            return

        try:
            with open(self.ruta_json, "r", encoding="utf-8") as f:
                usuarios = json.load(f)
        except Exception as e:
            print(f"❌ Error leyendo JSON usuarios: {e}")
            usuarios = []

        count = 0
        for usuario in usuarios:
            ruta_rostro = usuario.get("rostro")
            nombre = usuario.get("nombre", usuario.get("usuario", "Anonimo"))
            if not ruta_rostro:
                continue

            # Resolver ruta absoluta posible
            if not os.path.exists(ruta_rostro):
                alt = os.path.abspath(os.path.join(os.path.dirname(__file__), ruta_rostro))
                if os.path.exists(alt):
                    ruta_rostro = alt
                else:
                    print(f"   ❌ Archivo no existe: {ruta_rostro}")
                    continue

            try:
                # Importar DeepFace localmente (si está instalado)
                from deepface import DeepFace
                rep = DeepFace.represent(ruta_rostro, model_name=self.reconocimiento.modelo, enforce_detection=True)
                if isinstance(rep, list) and len(rep) > 0:
                    emb = np.array(rep[0]["embedding"], dtype=np.float32)
                    self.reconocimiento.known_face_encodings.append(emb)
                    self.reconocimiento.known_face_names.append(nombre)
                    count += 1
                    print(f"   ✅ Embedding añadido para {nombre}")
            except Exception as e:
                print(f"   ⚠️ No se pudo procesar {ruta_rostro}: {e}")

        # Guardar vectores extraídos en carpeta embeddings para uso futuro
        try:
            if count > 0:
                os.makedirs(self.embeddings_dir, exist_ok=True)
                embs = np.array(self.reconocimiento.known_face_encodings, dtype=np.float32)
                np.save(os.path.join(self.embeddings_dir, "embeddings.npy"), embs)
                with open(os.path.join(self.embeddings_dir, "nombres.json"), "w", encoding="utf-8") as f:
                    json.dump(self.reconocimiento.known_face_names, f, indent=4, ensure_ascii=False)
                print("🔄 Embeddings guardados en Datos/embeddings/")
        except Exception as e:
            print(f"⚠️ No se pudieron guardar embeddings extraídos: {e}")

        print(f"🎯 Finalizado. Embeddings cargados desde JSON: {count}")
        print("=" * 50)

    def iniciar_camara(self):
        """Inicia la cámara"""
        try:
            ok = self.camara.iniciar()
        except Exception as e:
            print(f"❌ Error iniciando cámara: {e}")
            ok = False

        if ok:
            self.timer.start(30)
            self.boton_iniciar.setEnabled(False)
            self.boton_detener.setEnabled(True)
            print("📹 CÁMARA INICIADA")
        else:
            self.label_video.setText("❌ No se pudo acceder a la cámara")
            print("❌ ERROR AL INICIAR CÁMARA")

    def actualizar_frame(self):
        """Obtiene frame, detecta y reconoce con embeddings cargados"""
        frame = self.camara.obtener_frame()
        if frame is None:
            return

        # Usar detector Haar para detección y luego embeddings para reconocimiento
        boxes, names = self.reconocimiento.reconocer_rostro(frame, umbral_coseno=0.45, usar_detector_haar=True)

        nombre_mostrar = "Desconocido"
        color_acceso = "red"
        rol = "VISITANTE"
        confianza_txt = ""

        for (top, right, bottom, left), name in zip(boxes, names):
            if name != "Desconocido":
                nombre_mostrar = name
                rol = "USUARIO REGISTRADO"
                color_acceso = "green"
                confianza_txt = ""
            else:
                nombre_mostrar = "Desconocido"
                rol = "VISITANTE"
                color_acceso = "red"

            color = (0, 255, 0) if color_acceso == "green" else (0, 0, 255)
            try:
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(frame, f"{nombre_mostrar}", (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            except Exception:
                pass

        # Actualizar UI
        self.nombre_detectado.setText(nombre_mostrar)
        self.lbl_rol.setText(rol)
        estado = "PERMITIDO" if color_acceso == "green" else "DENEGADO"
        self.lbl_estado.setText(estado)
        self.lbl_estado.setStyleSheet(f"color: {color_acceso};")

        # Mostrar frame en QLabel
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.label_video.setPixmap(QPixmap.fromImage(qt_image.scaled(
                self.label_video.width(), self.label_video.height(), Qt.KeepAspectRatio)))
        except Exception as e:
            print(f"❌ Error mostrando frame en UI: {e}")

    def detener_camara(self):
        """Detiene la cámara"""
        self.timer.stop()
        try:
            self.camara.detener()
        except Exception:
            pass
        self.label_video.clear()
        self.label_video.setText("Cámara detenida")
        self.boton_iniciar.setEnabled(True)
        self.boton_detener.setEnabled(False)
        print("⏹️ CÁMARA DETENIDA")

    def registrar_usuario(self):
        """
        Cierra la ventana principal y abre la nueva ventana de registro de usuario.
        """
        if 'VentanaRegistro' not in globals() or VentanaRegistro is None:
            QMessageBox.critical(
                self,
                "Error",
                "No se encontró la ventana de registro.\n"
                "Verifica que 'Interfaz/ventana_registro.py' exista y sea importable."
            )
            return

        try:
            self.ventana_registro = VentanaRegistro()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error al abrir ventana de registro",
                f"No se pudo crear la ventana de registro:\n{e}"
            )
            return

        try:
            self.ventana_registro.show()
            self.close()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error al mostrar ventana de registro",
                f"No se pudo mostrar la ventana de registro:\n{e}"
            )

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
        ruta_json = self.ruta_json

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
            if user.get("usuario") == usuario:
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


# Si deseas ejecutar esta ventana directamente para pruebas:
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())
