import cv2

# Iniciar la cámara (0 es el índice de la cámara predeterminada)
cap = cv2.VideoCapture(0)

while True:
    # Leer el cuadro de la cámara
    ret, frame = cap.read()

    if not ret:
        print("No se pudo acceder a la cámara.")
        break

    # Mostrar el cuadro en una ventana
    cv2.imshow('camara-Prueba', frame)

    # Salir si se presiona la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar la cámara y cerrar ventanas
cap.release()
cv2.destroyAllWindows()
