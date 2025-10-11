import cv2
import os
import face_recognition
import numpy as np

class ReconocimientoFacial:
    def __init__(self):
        # For detection, you can keep using Haar Cascade or use the face_recognition model
        self.detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        
        # Database to store known face encodings and their names
        self.known_face_encodings = []
        self.known_face_names = []
        
    def capturar_rostro(self, nombre_archivo="rostro.jpg"):
        # ... (keep your existing capture code, but ensure you save in color for recognition)
        # For recognition, it's better to save the image in color.
        # So, change this line when saving:
        # FROM: rostro_guardado = gris[y:y+h, x:x+w]
        # TO: rostro_guardado = frame[y:y+h, x:x+w] 
        pass
        
    def entrenar_desde_carpeta(self, carpeta_entrenamiento):
        """
        Trains the recognition model by loading known faces from a folder.
        Folder structure: /person_name/image1.jpg, /person_name/image2.jpg ...
        """
        for nombre_persona in os.listdir(carpeta_entrenamiento):
            carpeta_persona = os.path.join(carpeta_entrenamiento, nombre_persona)
            
            if os.path.isdir(carpeta_persona):
                for filename in os.listdir(carpeta_persona):
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                        ruta_imagen = os.path.join(carpeta_persona, filename)
                        
                        # Load and encode the image
                        imagen = face_recognition.load_image_file(ruta_imagen)
                        encodings = face_recognition.face_encodings(imagen)
                        
                        if len(encodings) > 0:
                            # Use the first face found in the image
                            self.known_face_encodings.append(encodings[0])
                            self.known_face_names.append(nombre_persona)
                            print(f"✅ Entrenado con: {nombre_persona} - {filename}")
                        else:
                            print(f"⚠️ No se encontró rostro en: {ruta_imagen}")
        
        print(f"🎯 Modelo entrenado con {len(self.known_face_encodings)} rostros de {len(set(self.known_face_names))} personas.")
    
    def reconocer_rostro(self, frame_unknown):
        """Recognizes faces in a given frame."""
        # Find all face locations and encodings in the current frame
        rgb_frame = cv2.cvtColor(frame_unknown, cv2.COLOR_BGR2RGB)
        
        # You can use face_recognition for detection as well for better accuracy
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        names = []
        for face_encoding in face_encodings:
            # Compare the current face with known faces
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.6)
            name = "Desconocido"
            
            # Find the best match
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
            
            names.append(name)
        
        return face_locations, names