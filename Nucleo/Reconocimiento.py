# Nucleo/Reconocimiento.py
"""
Reconocimiento facial basado en DeepFace (no usa dlib).
Clase: ReconocimientoFacial
Métodos principales usados por la UI:
 - capturar_rostro(ruta_destino) -> True/False (captura una imagen desde la cámara y la guarda)
 - entrenar_desde_carpeta(carpeta_entrenamiento) -> extrae embeddings y los guarda
 - cargar_vectores() -> carga vectores guardados (pickle)
 - reconocer_rostro(frame_bgr, umbral_coseno=0.45) -> (boxes, names)
 - detector -> Haar Cascade (para compatibilidad con el resto del código)
"""

import os
import cv2
import pickle
import numpy as np
from deepface import DeepFace
from datetime import datetime

RUTA_DATOS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Datos"))
RUTA_VECTORES = os.path.join(RUTA_DATOS, "vectores_deepface.pkl")
os.makedirs(RUTA_DATOS, exist_ok=True)

class ReconocimientoFacial:
    def __init__(self, modelo="Facenet"):
        # Detector Haar (se deja accesible para código que lo use directamente)
        self.detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        # Almacenamiento en memoria
        self.known_face_encodings = []  # lista de np.array embeddings
        self.known_face_names = []      # lista de nombres (strings)
        self.modelo = modelo

    # --------------------
    # Captura de rostro
    # --------------------
    def capturar_rostro(self, ruta_destino, mostrar_preview=False, cam_index=0, timeout_sec=7):
        """
        Abre la cámara, captura el primer frame que contenga un rostro detectado, guarda el recorte (BGR) en ruta_destino.
        Devuelve True si se guardó correctamente, False en caso contrario.
        """
        cap = cv2.VideoCapture(cam_index)
        if not cap.isOpened():
            print("❌ No se pudo abrir la cámara para captura.")
            return False

        inicio = datetime.now()
        guardado = False

        while (datetime.now() - inicio).total_seconds() < timeout_sec:
            ret, frame = cap.read()
            if not ret:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80,80))

            # Mostrar previsualización si se pide (no bloqueante)
            if mostrar_preview:
                try:
                    cv2.imshow("Captura - Alinee su rostro y presione 's' para guardar", frame)
                    k = cv2.waitKey(1) & 0xFF
                    if k == ord('s') and len(faces) > 0:
                        # guardar primer rostro detectado
                        x,y,w,h = faces[0]
                        rostro = frame[y:y+h, x:x+w]
                        cv2.imwrite(ruta_destino, rostro)
                        guardado = True
                        break
                    elif k == ord('q'):
                        break
                except Exception:
                    pass

            # Si detectó rostros, guardar el primero automáticamente
            if len(faces) > 0:
                x,y,w,h = faces[0]
                rostro = frame[y:y+h, x:x+w]
                # Guardar color BGR (para DeepFace)
                try:
                    cv2.imwrite(ruta_destino, rostro)
                    guardado = True
                except Exception as e:
                    print(f"❌ Error guardando imagen: {e}")
                break

        cap.release()
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass

        if guardado:
            print(f"📸 Rostro guardado en: {ruta_destino}")
        else:
            print("⚠️ No se capturó ningún rostro.")

        return guardado

    # --------------------
    # Entrenamiento desde carpeta (extrae embeddings)
    # --------------------
    def entrenar_desde_carpeta(self, carpeta_entrenamiento, guardar=True):
        """
        Carpeta con estructura: carpeta_entrenamiento/nombre_usuario/imagen.jpg
        Extrae 1 embedding por imagen válida y lo añade a la memoria.
        """
        carpeta_entrenamiento = os.path.abspath(carpeta_entrenamiento)
        if not os.path.isdir(carpeta_entrenamiento):
            print(f"⚠️ Carpeta de entrenamiento no encontrada: {carpeta_entrenamiento}")
            return

        count = 0
        for nombre_persona in sorted(os.listdir(carpeta_entrenamiento)):
            ruta_persona = os.path.join(carpeta_entrenamiento, nombre_persona)
            if not os.path.isdir(ruta_persona):
                continue
            for fname in os.listdir(ruta_persona):
                if not fname.lower().endswith((".png", ".jpg", ".jpeg")):
                    continue
                ruta_img = os.path.join(ruta_persona, fname)
                try:
                    # enforce_detection=True para asegurar que haya un rostro claro en las imágenes de entrenamiento
                    rep = DeepFace.represent(ruta_img, model_name=self.modelo, enforce_detection=True)
                    if isinstance(rep, list) and len(rep) > 0:
                        emb = np.array(rep[0]["embedding"], dtype=np.float32)
                        self.known_face_encodings.append(emb)
                        self.known_face_names.append(nombre_persona)
                        count += 1
                        print(f"✅ Embedding extraído: {nombre_persona} <- {fname}")
                except Exception as e:
                    print(f"⚠️ Omitida imagen {ruta_img}: {e}")

        if guardar:
            self._guardar_vectores()

        print(f"🎯 Entrenamiento completado. Embeddings extraídos: {count}")

    # --------------------
    # Cargar vectores desde disco
    # --------------------
    def cargar_vectores(self):
        if not os.path.exists(RUTA_VECTORES):
            print("ℹ️ No hay vectores guardados aún.")
            return
        try:
            with open(RUTA_VECTORES, "rb") as f:
                data = pickle.load(f)
            encs = data.get("encodings", [])
            names = data.get("names", [])
            self.known_face_encodings = [np.array(x, dtype=np.float32) for x in encs]
            self.known_face_names = names
            print(f"📥 Vectores cargados: {len(self.known_face_encodings)}")
        except Exception as e:
            print(f"❌ Error cargando vectores: {e}")

    def _guardar_vectores(self):
        data = {
            "encodings": [e.tolist() for e in self.known_face_encodings],
            "names": self.known_face_names
        }
        try:
            with open(RUTA_VECTORES, "wb") as f:
                pickle.dump(data, f)
            print(f"💾 Vectores guardados en: {RUTA_VECTORES}")
        except Exception as e:
            print(f"❌ Error guardando vectores: {e}")

    # --------------------
    # Reconocer en un frame (BGR)
    # --------------------
    def reconocer_rostro(self, frame_bgr, umbral_coseno=0.45, usar_detector_haar=True):
        """
        Recibe frame BGR, devuelve (boxes, names)
        boxes: lista de tuplas (top, right, bottom, left) — igual formato que face_recognition
        names: lista de strings (mismos índices que boxes)
        """
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)

        faces = []
        boxes = []

        if usar_detector_haar:
            rects = self.detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60,60))
            for (x, y, w, h) in rects:
                face = frame_bgr[y:y+h, x:x+w]
                faces.append(face)
                boxes.append((y, x+w, y+h, x))
        else:
            # Fallback: intentar representar la imagen completa (peor detección)
            faces.append(frame_bgr)
            boxes.append((0, frame_bgr.shape[1], frame_bgr.shape[0], 0))

        names = []
        for face_img, box in zip(faces, boxes):
            try:
                # Represent con enforce_detection=False para aceptar crops
                rep = DeepFace.represent(face_img, model_name=self.modelo, enforce_detection=False)
                if not isinstance(rep, list) or len(rep) == 0:
                    names.append("Desconocido")
                    continue
                emb = np.array(rep[0]["embedding"], dtype=np.float32)
            except Exception:
                names.append("Desconocido")
                continue

            if len(self.known_face_encodings) == 0:
                names.append("Desconocido")
                continue

            # Distancia coseno (entre 0 y 2, idealmente 0 para idénticos)
            def cosine(a, b):
                return 1 - (np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10))

            distances = [cosine(emb, k) for k in self.known_face_encodings]
            best_idx = int(np.argmin(distances))
            best_dist = distances[best_idx]

            if best_dist <= umbral_coseno:
                names.append(self.known_face_names[best_idx])
            else:
                names.append("Desconocido")

        return boxes, names