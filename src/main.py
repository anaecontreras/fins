import customtkinter
from tkinter import Image
import os
import sys
from PIL import Image
from pathlib import Path
from modulos.modulo1 import Modulo1
from modulos.modulo2 import Modulo2
from modulos.modulo3 import Modulo3

from colores import *

# FUNCIÓN PARA MANEJAR RUTAS DE RECURSOS
def resource_path(relative_path):
    """Obtiene la ruta correcta para recursos en desarrollo y producción"""
    try:
        # PyInstaller crea una carpeta temporal en _MEIPASS
        base_path = Path(sys._MEIPASS)
    except Exception:
        base_path = Path(__file__).parent.parent  # Raíz del proyecto en desarrollo
    
    # Construye la ruta completa
    full_path = base_path / relative_path
    
    # Verifica si existe en la ruta construida
    if full_path.exists():
        return str(full_path)
    
    # Si no existe, intenta con la ruta relativa directa
    alt_path = Path(relative_path)
    if alt_path.exists():
        return str(alt_path)
    
    # Si todo falla, devuelve la ruta esperada por PyInstaller
    return str(Path(sys._MEIPASS) / relative_path if hasattr(sys, '_MEIPASS') else str(base_path / relative_path))


# FUNCIONES PARA LLAMAR MODULOS
def llamar_modulo1():
    app.modulo1 = Modulo1(app)
    app.modulo1.grab_set()    # FOCO EXCLUSIVO
def llamar_modulo2():
    app.modulo2 = Modulo2(app)
    app.modulo2.grab_set()    # FOCO EXCLUSIVO
def llamar_modulo3():
    app.modulo3 = Modulo3(app)
    app.modulo3.grab_set()    # FOCO EXCLUSIVO
    

# TEMA DE LA APLICACION
customtkinter.set_appearance_mode("light")  # o "light", "dark"
# customtkinter.set_default_color_theme("green")  # o "blue", "dark-blue"

# VENTANA DE LA APLICACION
app = customtkinter.CTk()
app.overrideredirect(True)
label = customtkinter.CTkLabel(app, text='Factibilidad para Instalación de Nuevos Servicios', width=40, height=28, fg_color='transparent', font=("Arial", 24, "bold"))
label.pack(pady=10)

# SECCIONES DE LA APLICACION
frame_superior = customtkinter.CTkFrame(app, height=100, fg_color=color_fondo1, border_width=1, border_color="#221E1E")
frame_superior.pack(side="top", fill="x", padx=10, pady=10)
frame_inferior = customtkinter.CTkFrame(app, fg_color=color_fondo1, border_width=1, border_color="#221E1E")
frame_inferior.pack(side="top", fill="both", padx=10, pady=10, expand=True)

frame_inferior_izquierdo = customtkinter.CTkFrame(frame_inferior, fg_color=color_fondo2, border_width=1, border_color="#221E1E")
frame_inferior_izquierdo.pack(side="left", fill="both", expand=True, padx=10, pady=5)

frame_inferior_derecho = customtkinter.CTkFrame(frame_inferior, fg_color=color_fondo2, border_width=1, border_color="#221E1E")
frame_inferior_derecho.pack(side="left", fill="both", expand=True, padx=10, pady=5)

# Carga de imagen con manejo robusto
try:
    # Usar resource_path para obtener la ubicación correcta
    ruta_imagen = resource_path(os.path.join("assets", "logo.png"))
    
    if os.path.exists(ruta_imagen):
        my_image = customtkinter.CTkImage(
            light_image=Image.open(ruta_imagen),
            size=(680, 550)
        )
        image_label = customtkinter.CTkLabel(frame_inferior_izquierdo, image=my_image, text="")
        image_label.pack(pady=20)
    else:
        raise FileNotFoundError(f"Archivo no encontrado en: {ruta_imagen}")
except Exception as e:
    print(f"Error cargando imagen: {e}")
    # Crear imagen de error programática
    error_img = Image.new('RGB', (680, 550), color='#333333')
    my_image = customtkinter.CTkImage(
        light_image=error_img,
        size=(680, 550)
    )
    image_label = customtkinter.CTkLabel(
        frame_inferior_izquierdo, 
        image=my_image, 
        text=f"Imagen no encontrada\n{ruta_imagen}",
        text_color="white",
        compound="center",
        font=("Arial", 14)
    )
    image_label.pack(pady=20)

texto_largo1 = """
Desarrollado por Ana Contreras y Diana Sierra, 
estudiantes de Ingeniería en Informática en la Universidad Nacional Experimental de las Telecomunicaciones e Informática (UNETI), como parte de las prácticas laborales, Junio de 2025.

Tecnologías Utilizadas

Lenguaje: Python 3.8 
(32 Bits / Compatible Windows 7)

Librerías utilizadas: 

* CustomTkinter (para interfaces modernas)
* TkinterMapView (mapas interactivos)

* Pillow y PyScreeze (procesamiento de imágenes)
* OpenPyXL (manejo de Excel)
* Geopy y Geocoder (geolocalización)
* PyAutoGUI y MouseInfo (Automatización)
* Matplotlib, NumPy, SciPy (Ciencia de datos y gráficos)
* Requests (peticiones HTTP)
* ReportLab (generación de PDFs)

* PyInstaller (empaquetado de la aplicación 
con todas las dependencias)
"""

label_texto1 = customtkinter.CTkLabel(frame_inferior_derecho, text=texto_largo1, wraplength=400, justify="center", font=("Arial", 15, "bold"))
label_texto1.pack(padx=2, pady=(20, 0), fill="x")

# texto_largo2 = ("Tecnologías utilizadas: "
#                "Lenguaje de programación: Python 3.12.4 / Librerias: CustomTkinter 5.2.2, "
#                "Pillow 11.2.1")
# label_texto2 = customtkinter.CTkLabel(frame_inferior_derecho, text=texto_largo2, wraplength=400, justify="center", font=("Arial", 18, "bold"))
# label_texto2.pack(padx=2, pady=(35, 2), fill="x")

# BOTONES DEL MENU
frame_botones = customtkinter.CTkFrame(frame_superior, fg_color="transparent")
frame_botones.pack(pady=10)
button1 = customtkinter.CTkButton(frame_botones, text="Perfil Topográfico", command=llamar_modulo1, fg_color="#4c607c")
button2 = customtkinter.CTkButton(frame_botones, text="Nuevos Servicios", command=llamar_modulo2, fg_color="#4c607c")
button3 = customtkinter.CTkButton(frame_botones, text="Gestión Estaciones", command=llamar_modulo3, fg_color="#4c607c")
button4 = customtkinter.CTkButton(frame_botones, text="Salir", command=app.destroy, fg_color="#4c607c")
button1.pack(side="left", padx=15, pady=10)  
button2.pack(side="left", padx=15, pady=10)  
button3.pack(side="left", padx=15, pady=10)  
button4.pack(side="left", padx=15, pady=10)  


# AMPLIACION DE VENTANA 
app.after(0, lambda: app.state('zoomed'))
app.mainloop()


