# 🧠 Proyecto de Reconocimiento Facial

### 🎓 Proyecto de Grado – Aplicación de Escritorio con Python (PySide6 + OpenCV)

---

## 📘 Descripción General del Proyecto

El **Proyecto de Reconocimiento Facial** es una aplicación de escritorio desarrollada en **Python**, utilizando **PySide6** para la interfaz gráfica de usuario (GUI) y **OpenCV** para el procesamiento de imágenes y video en tiempo real.  
Su propósito es permitir el **reconocimiento facial automático** a través de la cámara del dispositivo, facilitando procesos como el **inicio de sesión**, **registro de usuarios** y **verificación de identidad** sin necesidad de introducir contraseñas.

El sistema está diseñado con una **arquitectura modular**, que separa la lógica del negocio, la interfaz y la gestión de datos, permitiendo una fácil expansión, mantenimiento y escalabilidad.  
Además, se prioriza una **interfaz intuitiva, profesional y adaptable**, acompañada de un estilo visual moderno basado en hojas de estilo `.qss`.

---

## 🚀 Objetivos del Proyecto

- Desarrollar una herramienta que permita la **detección, registro y autenticación de rostros humanos**.
- Implementar una **interfaz amigable y funcional**, optimizada para usuarios finales no técnicos.
- Diseñar una estructura de código **escalable y mantenible**, siguiendo buenas prácticas de desarrollo.
- Integrar una **base de datos local** para el almacenamiento seguro de usuarios y vectores faciales.
- Explorar el uso de **modelos de visión por computadora** para la detección facial eficiente en tiempo real.

---

## 🧩 Características Principales

- 📷 **Captura de video en tiempo real** usando la cámara del dispositivo con OpenCV.  
- 😎 **Detección y reconocimiento facial** mediante modelos Haarcascade o embeddings personalizados.  
- 🧑‍💼 **Registro de nuevos usuarios** con almacenamiento de imágenes y vectores de características.  
- 🔒 **Inicio de sesión facial o con credenciales convencionales.**  
- 🎨 **Interfaz moderna, personalizable y responsiva** usando PySide6 y estilos `.qss`.  
- 🗃️ **Base de datos** para gestionar usuarios, configuraciones y registros faciales.  
- ⚙️ **Código modular y documentado**, optimizado para futuras mejoras.  
- 💬 **Mensajes interactivos y notificaciones visuales** para mejorar la experiencia del usuario.  
- 🧠 **Posibilidad de integrar modelos avanzados** de reconocimiento facial como FaceNet o DeepFace.  

---
## 🧱 Estructura del Proyecto

```bash
reconocimiento_facial/
│
├── aplicacion/                          
│   ├── nucleo/                          
│   │   ├── camara.py                    ← Control de cámara y flujo de video
│   │   ├── reconocimiento.py            ← Detección y reconocimiento facial
│   │   ├── base_datos.py                ← Gestión y conexión con la base de datos
│   │   └── utilidades.py                ← Funciones auxiliares (logs, validaciones, etc.)
│   │
│   ├── interfaz/                        
│   │   ├── ventana_principal.py         ← Ventana principal de la app
│   │   ├── ventana_login.py             ← Pantalla de inicio de sesión
│   │   ├── ventana_registro.py          ← Pantalla de registro facial/usuario
│   │   └── estilos/
│   │       └── estilo.qss               ← Estilos globales (colores, fuentes, botones)
│   │
│   ├── modelos/                         
│   │   ├── usuario.py                   ← Clase Usuario (ID, nombre, vector facial)
│   │   └── configuracion.py             ← Configuraciones del sistema (rutas, cámara, etc.)
│   │
│   ├── recursos/                        
│   │   ├── iconos/                      ← Íconos, logos e imágenes
│   │   ├── modelos_xml/                 ← Modelos preentrenados (Haarcascade, etc.)
│   │   └── fuentes/                     ← Tipografías personalizadas
│   │
│   ├── main.py                          ← Punto de entrada principal
│   └── __init__.py                      
│
├── pruebas/                             
│   ├── prueba_camara.py
│   ├── prueba_reconocimiento.py
│   └── prueba_interfaz.py
│
├── datos/                               
│   ├── rostros/                         ← Imágenes de rostros capturados
│   ├── vectores/                        ← Vectores de características faciales
│   └── base_datos.db                    ← Base de datos 
│
├── requirements.txt                     ← Dependencias del proyecto
├── README.md                            ← Documentación general
└── .gitignore                           ← Archivos ignorados por Git
```


### 🗂️ Explicación de Carpetas

| Carpeta / Archivo | Función |
| ------------------ | -------- |
| `aplicacion/` | Código principal del programa. |
| `nucleo/` | Lógica central: cámara, reconocimiento, base de datos, etc. |
| `interfaz/` | Ventanas, formularios y estilos `.qss`. |
| `modelos/` | Clases de usuarios, configuraciones o entidades del sistema. |
| `recursos/` | Archivos estáticos (íconos, fuentes, modelos XML). |
| `pruebas/` | Pruebas unitarias y funcionales. |
| `datos/` | Archivos generados (fotos, vectores, base de datos). |
| `requirements.txt` | Lista de librerías requeridas. |
| `main.py` | Archivo principal que ejecuta la aplicación. |
| `README.md` | Documentación general del proyecto. |

---

## ⚙️ Instalación y Configuración

# 🧰 Requerimientos para ejecutar el programa

## 📌 Dependencias principales
- **Python:** `3.12.4`  
El programa está desarrollado y probado para esta versión.

---

## 🖥️ Dependencias del sistema

### Para sistemas basados en Debian/Ubuntu:
```bash
sudo apt-get update
sudo apt-get install -y python3-dev python3-pip build-essential cmake
sudo apt-get install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev
```

### Para Windows:
> Usar `pip` normalmente es suficiente para instalar las dependencias de Python.

---

## 🐍 Dependencias de Python

Crea un archivo **`requirements.txt`** con el siguiente contenido:

```
opencv-python
PySide6
numpy
deepface
```

---

## 📦 Instalación de dependencias

Instalar todas las dependencias de una sola vez:

```bash
pip install -r requirements.txt
```

O instalarlas individualmente (Mejor Opción):

```bash
pip install opencv-python
pip install PySide6
pip install numpy
pip install deepface
```


## ⚠️ Notas importantes

### Sobre DeepFace
- DeepFace instalará automáticamente dependencias como TensorFlow.
- La primera ejecución puede ser lenta, ya que descargará modelos pre-entrenados.
- Se recomienda buena conexión a internet para la primera ejecución.

### Compatibilidad
- Código probado con **Python 3.12.4**.
- Las versiones especificadas garantizan compatibilidad.
- Si hay problemas con **PySide6**, se puede usar **PyQt6** como alternativa.

### Recursos del sistema
- Mínimo **4 GB de RAM**.
- Cámara web funcionando.
- Espacio en disco para modelos de DeepFace (~500 MB).

---

## ▶️ Comando de ejecución

Desde el directorio principal del proyecto:

```bash
python Interfaz/Ventana_Principal.py
```

---

## 🧭 Solución de problemas comunes

Si encuentras errores:

- ✅ Verifica que todas las dependencias estén instaladas.  
- 🐍 Asegúrate de tener **Python 3.12.4**.  
- 📸 Revisa que la cámara web esté funcionando.  
- 🛡️ Ejecuta como administrador si hay problemas de permisos.


### 1️⃣ Clonar el repositorio

```bash
git clone https://github.com/<tu_usuario>/reconocimiento_facial.git
```
cd reconocimiento_facial
	done
### Crear y activar entorno virtual
``` bash
python -m venv venv
venv\Scripts\activate   # En Windows
```
#### Ejecutar la aplicación
``` bash
python aplicacion/main.py
```
### 🧰Tecnologia Utilizadas
| Componente       | Descripción                                        |
| ---------------- | -------------------------------------------------- |
| **Python 3.12+** | Lenguaje principal del proyecto                    |
| **PySide6**      | Framework para interfaces gráficas (Qt for Python) |
| **OpenCV**       | Biblioteca para visión por computadora             |
| **NumPy**        | Procesamiento numérico y matricial                 |
| **SQLite**       | Base de datos local integrada                      |

## 👥 Autores
| Nombre                             | Rol                                                   |
| ---------------------------------- | ----------------------------------------------------- |
| **Alejandro Atuesta**        | Desarrollador de la interfaz y lógica principal       |
| **Juan Cipamocha**                | Colaborador en interfaz y estructura visual           |
| **Edgar Burgos** | Desarrollador de funciones lógicas y gestión de datos |

### 🔮 Futuras Mejoras
🔐 Control de acceso por roles (Administrador / Usuario).
📦 Empaquetado en .exe (Windows).

