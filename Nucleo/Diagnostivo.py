# diagnostico.py
import cv2
import os
import json

def diagnosticar_sistema():
    print("🔍 DIAGNÓSTICO DEL SISTEMA DE RECONOCIMIENTO FACIAL")
    print("=" * 50)
    
    # 1. Verificar OpenCV
    print("1. Verificando OpenCV...")
    print(f"   OpenCV version: {cv2.__version__}")
    
    # 2. Verificar clasificador Haar
    print("2. Verificando clasificador Haar...")
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    if os.path.exists(cascade_path):
        print("   ✅ Clasificador Haar encontrado")
    else:
        print("   ❌ Clasificador Haar NO encontrado")
        return
    
    # 3. Verificar cámara
    print("3. Verificando cámara...")
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        print("   ✅ Cámara funcionando")
        cap.release()
    else:
        print("   ❌ No se puede acceder a la cámara")
    
    # 4. Verificar datos de usuarios
    print("4. Verificando datos de usuarios...")
    if os.path.exists("Datos/usuarios.json"):
        with open("Datos/usuarios.json", "r") as f:
            usuarios = json.load(f)
        print(f"   ✅ {len(usuarios)} usuarios registrados")
        
        for usuario in usuarios:
            if os.path.exists(usuario["rostro"]):
                print(f"      ✅ {usuario['nombre']}: {usuario['rostro']}")
            else:
                print(f"      ❌ {usuario['nombre']}: Archivo no encontrado")
    else:
        print("   ❌ No hay usuarios registrados")
    
    print("=" * 50)
    print("🔧 EJECUTA ESTE DIAGNÓSTICO SI TIENES PROBLEMAS")

if __name__ == "__main__":
    diagnosticar_sistema()