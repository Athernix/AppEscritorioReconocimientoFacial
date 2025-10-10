# Nucleo/Camara.py
import cv2  # Importar librería de OpenCV


def iniciar_video():
    """Inicia la cámara y muestra el video en una ventana hasta que se presione 'q'."""
    camara = cv2.VideoCapture(0)

    if not camara.isOpened():
        print("❌ No se pudo acceder a la cámara.")
        return

    print("✅ Cámara iniciada. Presiona 'q' para salir.")

    while True:
        ret, frame = camara.read()
        if not ret:
            print("Error al leer el cuadro de la cámara.")
            break

        # Mostrar el cuadro en una ventana
        cv2.imshow('Cámara - Prueba', frame)

        # Salir si se presiona la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Liberar recursos
    camara.release()
    cv2.destroyAllWindows()
