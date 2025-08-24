import tkinter as tk
from tkinter import ttk
import customtkinter
import tkintermapview
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

from tkinter import Event
import requests

import numpy as np
from scipy.interpolate import make_interp_spline
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib as mpl

from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image as PILImage

from colores import *



class Modulo1(customtkinter.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Perfil Topográfico")
        self.geometry("300x200")

        self.linea_ruta = None
        self.coords_origen = None
        self.coords_destino = None
        
        # Título principal
        label = customtkinter.CTkLabel(
            self, 
            text='Trazado de Perfil Topográfico', 
            width=40, 
            height=28, 
            fg_color='transparent', 
            font=("Arial", 24, "bold")
        )
        label.pack(pady=10)
        
        # Frame izquierdo (controles)
        self.frame_izquierdo = customtkinter.CTkFrame(
            self, 
            fg_color=color_fondo2, 
            border_width=1, 
            border_color="#221E1E", 
            width=200
        )
        self.frame_izquierdo.pack(side="left", fill="y", padx=10, pady=5)
        self.frame_izquierdo.pack_propagate(False)
        
        # Frame derecho (contenido principal)
        self.frame_derecho = customtkinter.CTkFrame(
            self, 
            fg_color=color_fondo2, 
            border_width=1, 
            border_color="#221E1E"
        )
        self.frame_derecho.pack(side="left", fill="both", expand=True, pady=5, padx=10)
        
        # Crear widgets
        self.crea_lado_izquierdo()
        self.crea_lado_derecho()
        self.crear_mapa_inicial()
        
        # Configuración de ventana
        self.after(0, lambda: self.state('zoomed'))
        self.overrideredirect(True)

    def crea_lado_izquierdo(self):
        """Crea los widgets del panel izquierdo (campos y botones)"""
        # Campos de entrada
        label_texto1 = customtkinter.CTkLabel(
            self.frame_izquierdo, 
            text="Punto Origen", 
            font=("Arial", 12, "bold")
        )
        label_texto1.pack(padx=2, pady=(25, 5), fill="x")
        self.punto_origen = customtkinter.CTkEntry(
            self.frame_izquierdo, 
            placeholder_text="Latitud y Longitud"
        )
        self.punto_origen.pack()
        
        label_texto2 = customtkinter.CTkLabel(
            self.frame_izquierdo, 
            text="Punto Destino", 
            font=("Arial", 12, "bold")
        )
        label_texto2.pack(padx=2, pady=(15, 5), fill="x")
        self.punto_destino = customtkinter.CTkEntry(
            self.frame_izquierdo, 
            placeholder_text="Latitud y Longitud"
        )
        self.punto_destino.pack()
        
        label_texto3 = customtkinter.CTkLabel(
            self.frame_izquierdo, 
            text="Antena Origen", 
            font=("Arial", 12, "bold")
        )
        label_texto3.pack(padx=2, pady=(25, 5), fill="x")
        self.antena_origen = customtkinter.CTkEntry(
            self.frame_izquierdo, 
            placeholder_text="Altura en Torre (Mts)"
        )
        self.antena_origen.pack()
        self.antena_origen.insert(0, "25")
        
        label_texto4 = customtkinter.CTkLabel(
            self.frame_izquierdo, 
            text="Antena Destino", 
            font=("Arial", 12, "bold")
        )
        label_texto4.pack(padx=2, pady=(25, 5), fill="x")
        self.antena_destino = customtkinter.CTkEntry(
            self.frame_izquierdo, 
            placeholder_text="Altura en Torre (Mts)"
        )
        self.antena_destino.pack()
        self.antena_destino.insert(0, "25")

        
        label_texto5 = customtkinter.CTkLabel(
            self.frame_izquierdo, 
            text="Frecuencia Operación", 
            font=("Arial", 12, "bold")
        )
        label_texto5.pack(padx=2, pady=(25, 5), fill="x")
        self.frecuencia_operacion = customtkinter.CTkEntry(
            self.frame_izquierdo, 
            placeholder_text="GHz"
        )
        self.frecuencia_operacion.pack()
        self.frecuencia_operacion.insert(0, "6.5")

        
        # Botones
        frame_botones = customtkinter.CTkFrame(
            self.frame_izquierdo, 
            fg_color="transparent"
        )
        frame_botones.pack(pady=20, padx=20, fill="both", expand=True)
        
        boton1 = customtkinter.CTkButton(
            frame_botones, 
            text="Trazar Perfil", 
            command=self.trazar_perfil, fg_color="#4c607c"
        )
        boton1.pack(side="top", pady=10, fill="x")
        
        boton2 = customtkinter.CTkButton(
            frame_botones, 
            text="Limpiar Datos", 
            command=self.limpiar_campos, fg_color="#4c607c"
        )
        boton2.pack(side="top", pady=10, fill="x")
        
        self.boton3 = customtkinter.CTkButton(
            frame_botones, 
            text="Generar PDF", 
            command=self.generar_pdf,
            state="disabled", fg_color="#4c607c"
        )
        self.boton3.pack(side="top", pady=10, fill="x") 

        boton4 = customtkinter.CTkButton(
            frame_botones, 
            text="Cerrar Módulo", 
            command=self.cerrar_modulo, fg_color="#4c607c"
        )
        boton4.pack(side="top", pady=10, fill="x")

    def generar_pdf(self):
        self.hacer_zoom()
        self.canvas.yview_moveto(0)

        """Genera un PDF profesional con el perfil topográfico y datos técnicos"""
        try:
            import datetime, tempfile, os
            from reportlab.lib.pagesizes import letter, landscape, portrait
            from reportlab.pdfgen import canvas
            from reportlab.lib.utils import ImageReader
            from PIL import Image, ImageGrab
            from tkinter import filedialog
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_agg import FigureCanvasAgg
            from io import BytesIO

            lat_origen, lon_origen = map(float, self.punto_origen.get().split(','))
            lat_destino, lon_destino = map(float, self.punto_destino.get().split(','))
            altura_origen = float(self.antena_origen.get())
            altura_destino = float(self.antena_destino.get())
            frecuencia = float(self.frecuencia_operacion.get())
            origen = (lat_origen, lon_origen)
            destino = (lat_destino, lon_destino)
            distancia_total = geodesic(origen, destino).km

            pdf_path = filedialog.asksaveasfilename(
                parent=self,
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Guardar Perfil Topográfico",
                initialfile=f"Perfil_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            )
            if not pdf_path:
                return

            c = canvas.Canvas(pdf_path)
            paginas_creadas = 0

            # === Página 1: MAPA ===
            c.setPageSize(landscape(letter))
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(landscape(letter)[0]/2, landscape(letter)[1]-50, "Vista de Plano con Enlace Propuesto")

            try:
                if hasattr(self, 'mapa'):
                    # Forzar visibilidad y esperar más tiempo
                    self.lift()                               # Trae ventana al frente
                    self.attributes('-topmost', True)         # Mantiene ventana en tope
                    self.update_idletasks()
                    self.after(800)                           # Espera más tiempo
                    self.attributes('-topmost', False)        # Ya no es tope
                    self.update()                             # Procesa eventos pendientes

                    self.update_idletasks()
                    self.after(200)
                    x1 = self.mapa.winfo_rootx()
                    y1 = self.mapa.winfo_rooty()
                    x2 = (x1 + self.mapa.winfo_width()) - 70
                    y2 = y1 + self.mapa.winfo_height()
                    map_img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                    extrema = map_img.getextrema()
                    is_black = all([ex[0] == 0 and ex[1] == 0 for ex in extrema])
                    if not is_black:
                        map_path = os.path.join(tempfile.gettempdir(), "map_temp.png")
                        map_img.save(map_path)
                        img = ImageReader(map_path)
                        img_w, img_h = img.getSize()
                        new_width = landscape(letter)[0] - 100
                        new_height = new_width * (img_h / img_w)
                        c.drawImage(img, 50, landscape(letter)[1] - new_height - 70, width=new_width, height=new_height)
                        os.remove(map_path)
                    else:
                        c.setFont("Helvetica", 12)
                        c.drawCentredString(landscape(letter)[0]/2, landscape(letter)[1]/2,
                                            "Error al capturar el mapa: imagen inválida (pantalla negra)")
            except Exception as e:
                c.setFont("Helvetica", 12)
                c.drawCentredString(landscape(letter)[0]/2, landscape(letter)[1]/2,
                                    f"Error al capturar el mapa: {str(e)}")
            c.showPage()

            # === Página 2: Datos ===
            c.setPageSize(portrait(letter))
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(portrait(letter)[0]/2, portrait(letter)[1]-50, "Cálculos del Enlace")
            c.setFont("Helvetica", 12)
            y = portrait(letter)[1] - 100
            c.drawString(50, y, f"• Punto Origen: {lat_origen:.6f}, {lon_origen:.6f}")
            c.drawString(300, y, f"• Altura Antena Origen: {altura_origen} m"); y -= 30
            c.drawString(50, y, f"• Punto Destino: {lat_destino:.6f}, {lon_destino:.6f}")
            c.drawString(300, y, f"• Altura Antena Destino: {altura_destino} m"); y -= 30
            c.drawString(50, y, f"• Frecuencia: {frecuencia} GHz")
            c.drawString(300, y, f"• Distancia Total: {distancia_total:.3f} km"); y -= 30
            c.drawString(50, y, f"• Azimut A→B: {self.azimut_a_b:.2f}°")
            c.drawString(300, y, f"• Azimut B→A: {self.azimut_b_a:.2f}°"); y -= 30
            c.drawString(50, y, f"• FSPL (Pérdida en espacio libre): {self.per_enlace:.2f} dB")
            c.setFont("Helvetica-Bold", 14)
            c.rect(30, 30, portrait(letter)[0]-60, portrait(letter)[1]-100)
            c.showPage(); paginas_creadas += 1

            # === Página 3: Perfil ===
            if hasattr(self, 'profile_data'):
                data = self.profile_data
                c.setPageSize(landscape(letter))
                c.setFont("Helvetica-Bold", 18)
                c.drawCentredString(landscape(letter)[0]/2, landscape(letter)[1]-50, f"Perfil Topográfico - {frecuencia} GHz")
                fig = Figure(figsize=(10, 5), dpi=100)
                ax = fig.add_subplot(111)
                ax.plot(data['x_smooth'], data['y_smooth'], color="green", linewidth=2, label="Terreno")
                ax.fill_between(data['x_smooth'], data['y_smooth'], data['min_elevation']-50, color="green", alpha=0.3)
                ax.fill_between(data['x_smooth'], data['fresnel_upper'], data['fresnel_lower'], color="purple", alpha=0.5, label="Fresnel")
                ax.plot(data['x_smooth'], data['line_of_sight'], color="yellow", linestyle="-", linewidth=1.5, label="Línea de vista")
                ax.vlines(data['x_origen'], data['elevations'][0], data['y_antena_origen'], color="blue", linestyle=":", linewidth=2)
                ax.scatter(data['x_origen'], data['y_antena_origen'], marker="^", color="blue", s=100, label="Origen")
                ax.vlines(data['x_destino'], data['elevations'][-1], data['y_antena_destino'], color="red", linestyle=":", linewidth=2)
                ax.scatter(data['x_destino'], data['y_antena_destino'], marker="^", color="red", s=100, label="Destino")
                ax.set_title("Perfil Topográfico")
                ax.set_xlabel("Distancia (km)")
                ax.set_ylabel("Altura (m)")
                ax.grid(True)
                ax.legend()
                buf = BytesIO()
                fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
                buf.seek(0)
                img = ImageReader(buf)
                img_w, img_h = img.getSize()
                new_width = landscape(letter)[0] - 100
                new_height = new_width * (img_h / img_w)
                c.drawImage(img, 50, landscape(letter)[1] - new_height - 80, width=new_width, height=new_height)
                buf.close()
                c.showPage(); paginas_creadas += 1

            # === PÁGINAS DE ALTURAS COMPLETAS ===
            if hasattr(self, 'profile_data'):
                distancias = self.profile_data['x_smooth']
                alturas = self.profile_data['y_smooth']
                datos_tabla = list(zip(distancias, alturas))  # ¡ya no se salta ningún punto!
                filas_por_pagina = 48

                def renderizar_tabla(datos, titulo):
                    c.setPageSize(portrait(letter))
                    c.setFont("Helvetica-Bold", 16)
                    c.drawCentredString(portrait(letter)[0]/2, portrait(letter)[1]-50, titulo)
                    c.setFont("Helvetica-Bold", 12)
                    y = portrait(letter)[1] - 90
                    c.drawString(160, y, "Distancia (km)")
                    c.drawString(380, y, "Altura (m)")
                    y -= 20
                    c.setFont("Helvetica", 11)
                    for d, a in datos:
                        if y < 50:
                            break
                        c.drawString(160, y, f"{d:.3f}")
                        c.drawString(380, y, f"{a:.1f}")
                        y -= 18
                    c.showPage()

                total_filas = len(datos_tabla)
                paginas_necesarias = (total_filas + filas_por_pagina - 1) // filas_por_pagina

                for i in range(paginas_necesarias):
                    inicio = i * filas_por_pagina
                    fin = inicio + filas_por_pagina
                    titulo = f"Tabla de Alturas Intermedias ({i+1} de {paginas_necesarias})"
                    renderizar_tabla(datos_tabla[inicio:fin], titulo)
                    paginas_creadas += 1

            c.setPageCompression(1)
            c.save()
            self.mostrar_messagebox_oscuro("Éxito", f"PDF generado correctamente:\n{pdf_path}")

        except Exception as e:
            self.mostrar_messagebox_oscuro("Error", f"Error al generar PDF:\n{str(e)}")




    def crea_lado_derecho(self):
        """Configura el frame derecho con scroll y mapa"""
        # Canvas de tkinter estándar (no CTkCanvas)
        self.canvas = tk.Canvas(self.frame_derecho)
        self.canvas = tk.Canvas(
        self.frame_derecho,
            bg=color_fondo2,  # Mismo color que los frames CTk en modo oscuro
            highlightthickness=0  # Elimina el borde
        )
        self.scrollbar = customtkinter.CTkScrollbar(
            self.frame_derecho, 
            orientation="vertical", 
            command=self.canvas.yview
        )
        
        # Frame desplazable
        self.scrollable_frame = customtkinter.CTkFrame(self.canvas, fg_color=color_fondo2)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        # Configurar scroll
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Empaquetar elementos
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

    def crear_mapa_inicial(self):
        """Configura el mapa interactivo con buscador"""
        # Frame para el buscador
        self.frame_busqueda = customtkinter.CTkFrame(
            self.scrollable_frame,
            height=40,
            fg_color=color_fondo2
        )
        self.frame_busqueda.pack(fill="x", padx=5, pady=5)
        
        # Barra de búsqueda
        self.busqueda_entry = customtkinter.CTkEntry(
            self.frame_busqueda,
            placeholder_text="Buscar localidad en Venezuela...",
            width=300
        )
        self.busqueda_entry.pack(side="left", padx=5)
        self.busqueda_entry.bind("<Return>", self.buscar_localidad)
        
        self.boton_buscar = customtkinter.CTkButton(
            self.frame_busqueda,
            text="Buscar",
            width=80,
            command=self.buscar_localidad, fg_color="#4c607c"
        )
        self.boton_buscar.pack(side="left", padx=5)

        self.boton_centrar_plano = customtkinter.CTkButton(
            self.frame_busqueda,
            text="Zoom",
            width=80,
            command=self.hacer_zoom,
            state="disabled", fg_color="#4c607c"
        )
        self.boton_centrar_plano.pack(side="left", padx=5)
        
        # Frame para el mapa
        self.frame_mapa = customtkinter.CTkFrame(self.scrollable_frame, width=1070, height=500, fg_color=color_fondo2)
        self.frame_mapa.pack(fill="both", expand=True, pady=(0, 10), padx=10)
        
        # Configurar el mapa
        self.mapa = tkintermapview.TkinterMapView(self.frame_mapa, corner_radius=0, width=1070, height=500)
        self.mapa.pack(fill="both", expand=True, padx=(10))
        
        # Centrar el mapa en Venezuela
        self.mapa.set_position(8.0, -66.0)
        self.mapa.set_zoom(6)
        
        # Configurar menú contextual
        self.configurar_menu_contextual()

    def configurar_menu_contextual(self):
        """Configura el menú contextual para capturar coordenadas"""
        # Eliminar menús existentes
        if hasattr(self.mapa, '_right_click_menu_commands'):
            self.mapa._right_click_menu_commands.clear()
        
        # Agregar opciones personalizadas
        self.mapa.add_right_click_menu_command(
            label="Capturar punto origen",
            command=lambda coords: self.capturar_coordenadas(coords, "origen"),
            pass_coords=True
        )
        
        self.mapa.add_right_click_menu_command(
            label="Capturar punto destino",
            command=lambda coords: self.capturar_coordenadas(coords, "destino"),
            pass_coords=True
        )

    def capturar_coordenadas(self, coords, tipo):
        """Coloca las coordenadas en el campo correspondiente y actualiza la línea"""
        lat, lon = coords
        texto_coords = f"{lat:.6f}, {lon:.6f}"
        
        if tipo == "origen":
            self.punto_origen.delete(0, "end")
            self.punto_origen.insert(0, texto_coords)
            mensaje = "Coordenadas de origen capturadas"
            color = "blue"
            self.coords_origen = (lat, lon)
        else:
            self.punto_destino.delete(0, "end")
            self.punto_destino.insert(0, texto_coords)
            mensaje = "Coordenadas de destino capturadas"
            color = "red"
            self.coords_destino = (lat, lon)
        
        # Actualizar marcador
        if hasattr(self, f'marcador_{tipo}'):
            self.mapa.delete(getattr(self, f'marcador_{tipo}'))
            
        marcador = self.mapa.set_marker(
            lat, lon,
            text=f"Punto {tipo.capitalize()}",
            marker_color_circle=color,
            marker_color_outside=color,
            text_color="black"
        )
        setattr(self, f'marcador_{tipo}', marcador)
        
        # Dibujar o actualizar la línea si tenemos ambos puntos
        self.actualizar_linea_ruta()
        
        self.mostrar_mensaje_temporal(mensaje)

    def actualizar_linea_ruta(self):
        """Dibuja o actualiza la línea entre origen y destino"""
        # Eliminar línea existente
        if self.linea_ruta is not None:
            self.mapa.delete(self.linea_ruta)
        
        # Verificar si tenemos ambos puntos
        if self.coords_origen and self.coords_destino:
            lat_origen, lon_origen = self.coords_origen
            lat_destino, lon_destino = self.coords_destino
            
            # Crear nueva línea
            self.linea_ruta = self.mapa.set_path(
                [
                    (lat_origen, lon_origen),
                    (lat_destino, lon_destino),
                ],
                color="#000000",  # Aquí defines el color de la línea
                width=2
            )

    def mostrar_mensaje_temporal(self, mensaje):
        """Muestra un mensaje temporal en el mapa"""
        if hasattr(self, 'label_mensaje'):
            self.label_mensaje.destroy()
            
        self.label_mensaje = customtkinter.CTkLabel(
            self.mapa,
            text=mensaje,
            font=("Arial", 12),
            fg_color="#333333",
            text_color="white",
            corner_radius=5
        )
        self.label_mensaje.place(relx=0.5, rely=0.1, anchor="n")
        self.after(2000, lambda: self.label_mensaje.destroy())

    def hacer_zoom(self):
        """Ajusta el zoom del mapa para que todos los marcadores sean visibles"""
        # Obtener todos los marcadores del mapa
        marcadores = self.mapa.canvas_marker_list
        
        # Si no hay marcadores, no hacer nada
        if not marcadores:
            self.mostrar_mensaje_temporal("No hay marcadores para hacer zoom")
            return
        
        # Obtener todas las coordenadas de los marcadores
        coordenadas = []
        for marcador in marcadores:
            if hasattr(marcador, 'position'):
                lat, lon = marcador.position
                coordenadas.append((lat, lon))
        
        # Si tenemos la línea de ruta, añadir sus puntos también
        if self.linea_ruta is not None and hasattr(self.linea_ruta, 'position_list'):
            coordenadas.extend(self.linea_ruta.position_list)
        
        # Si no hay coordenadas válidas, salir
        if not coordenadas:
            return
        
        # Calcular los límites del área a mostrar
        lats = [coord[0] for coord in coordenadas]
        lons = [coord[1] for coord in coordenadas]
        
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)
        
        # Calcular el centro del área
        center_lat = (min_lat + max_lat) / 2
        center_lon = (min_lon + max_lon) / 2
        
        # Calcular el zoom apropiado basado en la extensión del área
        lat_diff = max_lat - min_lat
        lon_diff = max_lon - min_lon
        max_diff = max(lat_diff, lon_diff)
        
        # Mapear la diferencia a un nivel de zoom (ajustar estos valores según necesidad)
        if max_diff < 0.01:
            zoom_level = 15  # Muy cercano
        elif max_diff < 0.05:
            zoom_level = 13
        elif max_diff < 0.1:
            zoom_level = 11
        elif max_diff < 0.5:
            zoom_level = 9
        elif max_diff < 1:
            zoom_level = 7
        elif max_diff < 2:
            zoom_level = 6
        elif max_diff < 5:
            zoom_level = 5
        else:
            zoom_level = 4  # Muy lejano
        
        # Aplicar el zoom
        self.mapa.set_position(center_lat, center_lon)
        self.mapa.set_zoom(zoom_level)
        
        # Mostrar mensaje temporal
        self.mostrar_mensaje_temporal(f"Zoom ajustado a nivel {zoom_level}")

    def buscar_localidad(self, event=None):
        """Busca una localidad en el mapa"""
        localidad = self.busqueda_entry.get().strip()
        if not localidad:
            return
            
        try:
            geolocator = Nominatim(user_agent="fins_app")
            location = geolocator.geocode(localidad + ", Venezuela")
            
            if location:
                lat, lon = location.latitude, location.longitude
                self.mapa.set_position(lat, lon)
                self.mapa.set_zoom(15)
            else:
                self.mostrar_messagebox_oscuro("Error", "Localidad no encontrada")
        except Exception as e:
            self.mostrar_messagebox_oscuro("Error", f"Error de conexión: {str(e)}")

    def mostrar_messagebox_oscuro(self, titulo, mensaje):
        """Muestra un mensaje emergente con estilo oscuro"""
        ventana = customtkinter.CTkToplevel()
        ventana.geometry("300x150")
        ventana.title(titulo)
        ventana.configure(fg_color="#222222")
        etiqueta = customtkinter.CTkLabel(ventana, text=mensaje, text_color="white")
        etiqueta.pack(pady=20)
        boton = customtkinter.CTkButton(ventana, text="OK", command=ventana.destroy, fg_color="#4c607c")
        boton.pack(pady=10)
        ventana.grab_set()
        ventana.overrideredirect(True)

    def limpiar_perfil(self):

        # Eliminar el frame del perfil si existe
        if hasattr(self, 'frame_perfil'):
            self.frame_perfil.pack_forget()
            self.frame_perfil.destroy()
            del self.frame_perfil
        # Eliminar el frame de la tabla si existe
        if hasattr(self, 'frame_tabla_perfil'):
            self.frame_tabla_perfil.pack_forget()
            self.frame_tabla_perfil.destroy()
            del self.frame_tabla_perfil
        # Eliminar el frame de la tabla de calculos si existe
        if hasattr(self, 'frame_calculos'):
            self.frame_calculos.pack_forget()
            self.frame_calculos.destroy()
            del self.frame_calculos



    def limpiar_campos(self):
        self.canvas.yview_moveto(0)
        # Centrar el mapa en Venezuela
        self.mapa.set_position(8.0, -66.0)
        self.mapa.set_zoom(6)


        self.boton3.configure(state="disabled")
        self.boton_centrar_plano.configure(state="disabled")

        """Limpia todos los campos de entrada, marcadores y línea"""
        self.punto_origen.delete(0, "end")
        self.punto_destino.delete(0, "end")
        self.antena_origen.delete(0, "end")
        self.antena_origen.insert(0, "25")
        self.antena_destino.delete(0, "end")
        self.antena_destino.insert(0, "25")
        self.frecuencia_operacion.delete(0, "end")
        self.frecuencia_operacion.insert(0, "6.5")
        self.busqueda_entry.delete(0,"end")

        # Limpiar marcadores y línea del mapa
        self.mapa.delete_all_marker()
        self.coords_origen = None
        self.coords_destino = None
        
        # Eliminar el frame del perfil si existe
        if hasattr(self, 'frame_perfil'):
            self.frame_perfil.pack_forget()
            self.frame_perfil.destroy()
            del self.frame_perfil
        
        # Eliminar el frame de la tabla si existe
        if hasattr(self, 'frame_tabla_perfil'):
            self.frame_tabla_perfil.pack_forget()
            self.frame_tabla_perfil.destroy()
            del self.frame_tabla_perfil

        # Eliminar el frame de la tabla de calculos si existe
        if hasattr(self, 'frame_calculos'):
            self.frame_calculos.pack_forget()
            self.frame_calculos.destroy()
            del self.frame_calculos

        if hasattr(self, 'linea_ruta') and self.linea_ruta is not None:
            self.linea_ruta.delete()  # Borra la línea del mapa
            self.linea_ruta = None    # Opcional: limpiar la referencia
    

    def cerrar_modulo(self):
        try:
            # Detener cualquier proceso en segundo plano primero
            if hasattr(self, 'mapa'):
                self.mapa.delete_all_marker()
                self.mapa.set_position(0, 0)  # Resetear el mapa
                self.mapa.destroy()
            
            # Limpiar matplotlib para evitar fugas de memoria
            plt.close('all')
            
            # Liberar el foco antes de destruir
            self.grab_release()
            
            # Destruir la ventana
            self.destroy()
            
            # Reactivar la ventana principal
            if self.master is not None:
                self.master.deiconify()
                self.master.focus_force()
                
        except Exception as e:
            print(f"Error al cerrar el módulo: {e}")

        

    def trazar_perfil(self):
        self.limpiar_perfil()
        self.boton_centrar_plano.configure(state="normal")
        """Traza el perfil topográfico entre origen y destino"""
        # Validar campos
        if not all([
            self.punto_origen.get().strip(),
            self.punto_destino.get().strip(),
            self.antena_origen.get().strip(),
            self.antena_destino.get().strip(),
            self.frecuencia_operacion.get().strip()
        ]):
            self.mostrar_messagebox_oscuro("ERROR", "Debe completar todos los campos")
            return

        try:
            self.calculos_extras()
            self.boton3.configure(state="normal")
            # Obtener coordenadas de origen y destino
            lat_origen, lon_origen = map(float, self.punto_origen.get().split(','))
            lat_destino, lon_destino = map(float, self.punto_destino.get().split(','))
            
            origen = (lat_origen, lon_origen)
            destino = (lat_destino, lon_destino)
            
            # Obtener alturas de antenas y frecuencia
            altura_origen = float(self.antena_origen.get())
            altura_destino = float(self.antena_destino.get())
            frecuencia = float(self.frecuencia_operacion.get())
            
            # Crear frame para los cálculos (antes del frame del gráfico)
            self.frame_calculos = customtkinter.CTkFrame(
                self.scrollable_frame,
                fg_color=color_fondo1,
                height=100
            )
            self.frame_calculos.pack(fill="x", pady=(10, 0), padx=10)
            
            # Calcular distancia total
            distancia_total = geodesic(origen, destino).km
            
            # Crear grid para organizar la información
            self.frame_calculos.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
            
            # Mostrar coordenadas de origen
            label_origen = customtkinter.CTkLabel(
                self.frame_calculos,
                text=f"Punto de Origen: {lat_origen:.6f}, {lon_origen:.6f}",
                font=("Arial", 12, "bold"),
                text_color="#ffffff"
            )
            label_origen.grid(row=0, column=0, padx=10, pady=5, sticky="w")
            
            # Mostrar coordenadas de destino
            label_destino = customtkinter.CTkLabel(
                self.frame_calculos,
                text=f"Punto de Destino: {lat_destino:.6f}, {lon_destino:.6f}",
                font=("Arial", 12, "bold"),
                text_color="#ffffff"
            )
            label_destino.grid(row=0, column=1, padx=10, pady=5, sticky="w")
            
            # Mostrar distancia total
            label_distancia = customtkinter.CTkLabel(
                self.frame_calculos,
                text=f"Distancia total enlace propuesto: {distancia_total:.3f} km",
                font=("Arial", 12, "bold"),
                text_color="#ffffff"
            )
            label_distancia.grid(row=0, column=2, padx=10, pady=5, sticky="w")

            # Mostrar frecuencia
            label_frecuencia = customtkinter.CTkLabel(
                self.frame_calculos,
                text=f"Frecuencia: {frecuencia} GHz",
                font=("Arial", 12, "bold"),
                text_color="#ffffff"
            )
            label_frecuencia.grid(row=0, column=3, padx=10, pady=5, sticky="w")
            
            # Mostrar alturas de antenas
            label_altura_origen = customtkinter.CTkLabel(
                self.frame_calculos,
                text=f"Altura Antena Origen={altura_origen} Mts",
                font=("Arial", 12, "bold"),
                text_color="#ffffff"
            )
            label_altura_origen.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="w")

            # Mostrar alturas de antenas
            label_altura_destino = customtkinter.CTkLabel(
                self.frame_calculos,
                text=f"Altura Antena Destino={altura_destino} Mts",
                font=("Arial", 12, "bold"),
                text_color="#ffffff"
            )
            label_altura_destino.grid(row=1, column=1, columnspan=2, padx=10, pady=5, sticky="w")

            # Mostrar per del enlace
            label_per = customtkinter.CTkLabel(
                self.frame_calculos,
                text=f"FSPL (Perdida Espacio Libre)={self.per_enlace:.3f} dB",
                font=("Arial", 12, "bold"),
                text_color="#ffffff"
            )
            label_per.grid(row=1, column=2, columnspan=2, padx=10, pady=5, sticky="w")

            # Mostrar azimut a-b del enlace
            label_azimutab = customtkinter.CTkLabel(
                self.frame_calculos,
                text=f"Azimut A-B={self.azimut_a_b:.3f} º",
                font=("Arial", 12, "bold"),
                text_color="#ffffff"
            )
            label_azimutab.grid(row=1, column=3, columnspan=2, padx=10, pady=5, sticky="w")

            self.azimut_contrario = 180 - self.azimut_a_b

            # Mostrar azimut b-a del enlace
            label_azimutab = customtkinter.CTkLabel(
                self.frame_calculos,
                text=f"Azimut B-A={self.azimut_contrario:.3f} º",
                font=("Arial", 12, "bold"),
                text_color="#ffffff"
            )
            label_azimutab.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")
            
            
            # Crear frame para el gráfico (debajo del frame de cálculos)
            self.frame_perfil = customtkinter.CTkFrame(
                self.scrollable_frame,
                fg_color=color_fondo1,
                height=350
            )
            self.frame_perfil.pack(fill="x", pady=(10, 0))
            
            # Crear frame para la tabla
            self.frame_tabla_perfil = customtkinter.CTkFrame(
                self.scrollable_frame,
                fg_color=color_fondo2,
                height=300
            )
            self.frame_tabla_perfil.pack(fill="both", expand=True, pady=(0, 10))
            
            # Llamar a la función de trazado del perfil
            self.plot_profile_and_table(
                self.frame_perfil,
                self.frame_tabla_perfil,
                origen,
                destino,
                altura_origen,
                altura_destino,
                frecuencia
            )
            
        except Exception as e:
            self.mostrar_messagebox_oscuro("Error", f"No se pudo trazar el perfil: {str(e)}")

    def plot_profile_and_table(self, frame_graph, frame_table, origen, destino, altura_antena_origen, altura_antena_destino, frecuencia_GHz):
        """Genera el gráfico del perfil y la tabla de alturas"""

        # 🧹 Limpieza previa
        if hasattr(self, 'profile_canvas'):
            self.profile_canvas.get_tk_widget().destroy()
            del self.profile_canvas

        for widget in frame_graph.winfo_children():
            widget.destroy()
        for widget in frame_table.winfo_children():
            widget.destroy()

        # 🧹 Limpieza de figuras anteriores
        try:
            plt.close('all')  # Si no estás usando más figuras activas de matplotlib
        except Exception as e:
            print(f"Error cerrando figuras matplotlib: {e}")
            mpl.rcdefaults()

        # 🔧 Parámetros base
        c = 3e8
        frecuencia_Hz = frecuencia_GHz * 1e9
        wavelength_m = c / frecuencia_Hz

        # 🔄 Interpolación de puntos
        def interpolate_points(start, end, max_points=95):
            total_dist_km = geodesic(start, end).km
            num_points = min(int(total_dist_km / 0.1) + 1, max_points)
            lats = np.linspace(start[0], end[0], num_points)
            lons = np.linspace(start[1], end[1], num_points)
            return list(zip(lats, lons))

        points = interpolate_points(origen, destino)

        # 📡 Obtener elevaciones
        def get_elevations(points):
            base_url = "https://api.opentopodata.org/v1/srtm30m"
            locations_str = "|".join(f"{lat},{lon}" for lat, lon in points)
            url = f"{base_url}?locations={locations_str}"
            response = requests.get(url)
            if response.status_code != 200:
                raise Exception(f"Error en la API: {response.status_code}")
            data = response.json()
            return [result["elevation"] for result in data["results"]]

        elevations = get_elevations(points)

        # 📏 Calcular distancias acumuladas
        distances = [0]
        for i in range(1, len(points)):
            dist = geodesic(points[i - 1], points[i]).km
            distances.append(distances[-1] + dist)

        distances = np.array(distances)
        elevations = np.array(elevations)
        x_smooth = np.linspace(distances.min(), distances.max(), 300)
        spline = make_interp_spline(distances, elevations, k=3)
        y_smooth = spline(x_smooth)

        # 🔭 Línea de vista
        x_origen, x_destino = distances[0], distances[-1]
        y_antena_origen = elevations[0] + altura_antena_origen
        y_antena_destino = elevations[-1] + altura_antena_destino
        line_of_sight = np.interp(x_smooth, [x_origen, x_destino], [y_antena_origen, y_antena_destino])

        # 🌐 Zona de Fresnel
        def fresnel_radius(d1, d2, wavelength_m):
            d1_m, d2_m = d1 * 1000, d2 * 1000
            total_m = d1_m + d2_m
            return np.sqrt((wavelength_m * d1_m * d2_m) / total_m)

        fresnel_upper, fresnel_lower = [], []
        for x in x_smooth:
            d1 = x - x_origen
            d2 = x_destino - x
            if d1 < 0 or d2 < 0:
                fresnel_upper.append(np.nan)
                fresnel_lower.append(np.nan)
            else:
                r = fresnel_radius(d1, d2, wavelength_m)
                idx = np.abs(x_smooth - x).argmin()
                los_height = line_of_sight[idx]
                fresnel_upper.append(los_height + r)
                fresnel_lower.append(los_height - r)

        fresnel_upper = np.array(fresnel_upper)
        fresnel_lower = np.array(fresnel_lower)

        # 📊 Crear gráfico
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(12, 5))
        fig.patch.set_facecolor(color_fondo1)
        ax.set_facecolor(color_fondo2)

        # 📊 Configuración de ejes (AGREGAR ESTO ANTES DE CREAR EL GRÁFICO)
        # ax.set_xlim([0, distances[-1]])  # Límites del eje X (desde 0 hasta la distancia total)
        # ax.set_ylim([min(elevations) - 50, max(line_of_sight) + 50])  # Límites del eje Y

        # Personalización adicional de ejes:
        ax.tick_params(axis='both', colors='#ffffff')  # Color de las marcas de los ejes
        ax.xaxis.label.set_color('#ffffff')  # Color de la etiqueta del eje X
        ax.yaxis.label.set_color('#ffffff')  # Color de la etiqueta del eje Y

        ax.plot(x_smooth, y_smooth, color="#39C527", linewidth=2, label="Terreno")
        ax.fill_between(x_smooth, y_smooth, min(elevations) - 50, color="#39C527", alpha=0.3)
        ax.fill_between(x_smooth, fresnel_upper, fresnel_lower, color="#ff00ff", alpha=0.5, label="Fresnel")
        ax.plot(x_smooth, line_of_sight, color="#ffff00", linestyle="-", linewidth=1.5, label="Línea de vista")

        ax.vlines(x_origen, elevations[0], y_antena_origen, color="#0d1cec", linewidth=2, linestyle=":")
        ax.scatter(x_origen, y_antena_origen, marker="^", color="#0d1cec", s=100, label="Origen")
        ax.vlines(x_destino, elevations[-1], y_antena_destino, color="#cf0d0d", linewidth=2, linestyle=":")
        ax.scatter(x_destino, y_antena_destino, marker="^", color="#cf0d0d", s=100, label="Destino")

        ax.set_title(f"Perfil Topográfico - {frecuencia_GHz} GHz", color="white")
        ax.set_xlabel("Distancia (km)", color="white")
        ax.set_ylabel("Altura (m)", color="white")
        ax.grid(True, color="#000000")
        ax.legend()

        # Mostrar en tkinter
        self.profile_canvas = FigureCanvasTkAgg(fig, master=frame_graph)
        self.profile_canvas.draw()
        self.profile_canvas.get_tk_widget().pack(fill="both", expand=True)

        # 🗂️ Crear tabla
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background=color_fondo2, foreground="#000000", rowheight=25, fieldbackground="#ffffff")
        style.configure("Treeview.Heading", background=color_fondo2, foreground="#000000", font=('Arial', 10, 'bold'))
        style.map("Treeview", background=[('selected', '#22559b')])

        table = ttk.Treeview(frame_table, columns=("Distancia (km)", "Altura (m)"), show="headings", height=10)
        table.heading("Distancia (km)", text="Distancia (km)")
        table.heading("Altura (m)", text="Altura (m)")
        table.column("Distancia (km)", width=150, anchor="center")
        table.column("Altura (m)", width=150, anchor="center")

        for d, e in zip(distances, elevations):
            table.insert("", "end", values=(f"{d:.3f}", f"{e:.1f}"))

        scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=scrollbar.set)

        table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Guardar perfil (opcional)
        self.profile_data = {
            "x_smooth": x_smooth,
            "y_smooth": y_smooth,
            "fresnel_upper": fresnel_upper,
            "fresnel_lower": fresnel_lower,
            "line_of_sight": line_of_sight,
            "x_origen": x_origen,
            "x_destino": x_destino,
            "y_antena_origen": y_antena_origen,
            "y_antena_destino": y_antena_destino,
            "elevations": elevations,
            "min_elevation": min(elevations)
        }

        return distances[-1]

    
    def calculos_extras(self):
        """Realiza cálculos adicionales después del trazado del perfil"""
        # Validar campos primero (reutilizando la validación existente)
        if not all([
            self.punto_origen.get().strip(),
            self.punto_destino.get().strip(),
            self.antena_origen.get().strip(),
            self.antena_destino.get().strip(),
            self.frecuencia_operacion.get().strip()
        ]):
            self.mostrar_messagebox_oscuro("ERROR", "Debe completar todos los campos")
            return False

        try:
            # Obtener datos de los campos
            lat_origen, lon_origen = map(float, self.punto_origen.get().split(','))
            lat_destino, lon_destino = map(float, self.punto_destino.get().split(','))
            altura_origen = float(self.antena_origen.get())
            altura_destino = float(self.antena_destino.get())
            frecuencia = float(self.frecuencia_operacion.get())
            
            # Calcular distancia total
            origen = (lat_origen, lon_origen)
            destino = (lat_destino, lon_destino)
            distancia_total_km = geodesic(origen, destino).km
            
            # 1. Cálculo de Pérdida en Espacio Libre (FSPL)
            # Fórmula: FSPL (dB) = 20log10(d) + 20log10(f) + 32.45
            # donde d = distancia en km, f = frecuencia en MHz
            frecuencia_MHz = frecuencia * 1000
            self.per_enlace = 20 * np.log10(distancia_total_km) + 20 * np.log10(frecuencia_MHz) + 32.45
            
            # 2. Cálculo de Azimuts (sentido origen-destino y viceversa)
            def calcular_azimut(punto1, punto2):
                """Calcula el azimut entre dos puntos geográficos"""
                lat1, lon1 = np.radians(punto1[0]), np.radians(punto1[1])
                lat2, lon2 = np.radians(punto2[0]), np.radians(punto2[1])
                
                dlon = lon2 - lon1
                x = np.sin(dlon) * np.cos(lat2)
                y = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(dlon)
                
                azimut = np.degrees(np.arctan2(x, y))
                return (azimut + 360) % 360  # Normalizar a 0-360°
            
            self.azimut_a_b = calcular_azimut(origen, destino)
            self.azimut_b_a = calcular_azimut(destino, origen)
            
            # Mostrar resultados en la interfaz (opcional)
            # self.mostrar_resultados_calculos()
            
            return True
            
        except Exception as e:
            self.mostrar_messagebox_oscuro("Error en cálculos", f"Error: {str(e)}")
            return False