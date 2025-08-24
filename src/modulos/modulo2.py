import customtkinter
import tkintermapview
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from tkinter import Event, ttk

from reportlab.lib.pagesizes import letter, landscape, portrait
from reportlab.lib.units import inch

from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image as PILImage
import tempfile
import os
import pyautogui
from PIL import ImageGrab

from util.db import obtener_todas

from colores import *

class Modulo2(customtkinter.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Nuevos Servicios")
        self.geometry("300x200")
        label = customtkinter.CTkLabel(self, text='Nuevos Servicios', width=40, height=28, fg_color='transparent', font=("Arial", 24, "bold"))
        label.pack(pady=10)

        # SECCIONES
        self.frame_izquierdo = customtkinter.CTkFrame(self, fg_color=color_fondo2, border_width=1, border_color="#221E1E", width=200)
        self.frame_izquierdo.pack(side="left", fill="y", padx=10, pady=5)
        self.frame_izquierdo.pack_propagate(False)

        self.frame_derecho = customtkinter.CTkFrame(self, fg_color=color_fondo2, border_width=1, border_color="#221E1E")
        self.frame_derecho.pack(side="left", fill="both", expand=True, pady=5, padx=10)

        # ETIQUETAS E INPUT LADO IZQUIERDO
        label_texto1 = customtkinter.CTkLabel(self.frame_izquierdo, text="Sitio Propuesto", font=("Arial", 12, "bold"))
        label_texto1.pack(padx=2, pady=(65, 5), fill="x")
        self.punto_propuesto = customtkinter.CTkEntry(self.frame_izquierdo, placeholder_text="Latitud y Longitud")
        self.punto_propuesto.pack()
        
        # Vincular evento para mantener el foco
        self.punto_propuesto.bind("<FocusOut>", self.mantener_foco)

        label_texto2 = customtkinter.CTkLabel(self.frame_izquierdo, text="Rango Distancia", font=("Arial", 12, "bold"))
        label_texto2.pack(padx=2, pady=(15, 5), fill="x")
        self.rango = customtkinter.CTkEntry(self.frame_izquierdo, placeholder_text="Rango (Kms)")
        self.rango.pack()

        frame_botones = customtkinter.CTkFrame(self.frame_izquierdo, fg_color="transparent")
        frame_botones.pack(pady=20, padx=20, fill="both", expand=True)
        boton1 = customtkinter.CTkButton(frame_botones, text="Hacer Estudio", command=self.hacer_estudio, fg_color="#4c607c")
        boton1.pack(side="top", pady=10, fill="x")
        boton2 = customtkinter.CTkButton(frame_botones, text="Limpiar Datos", command=self.limpiar_campos, fg_color="#4c607c")
        boton2.pack(side="top", pady=10, fill="x")
        self.boton3 = customtkinter.CTkButton(frame_botones, text="Generar PDF", command=self.generar_pdf, state="disabled", fg_color="#4c607c")
        self.boton3.pack(side="top", pady=10, fill="x")
        boton4 = customtkinter.CTkButton(frame_botones, text="Cerrar Módulo", command=self.cerrar_modulo, fg_color="#4c607c")
        boton4.pack(side="top", pady=10, fill="x")

        # Crear mapa de Venezuela al iniciar
        self.crear_mapa_inicial()

        # AMPLIACION DE VENTANA 
        self.after(0, lambda: self.state('zoomed'))
        self.overrideredirect(True)

    def mostrar_messagebox_oscuro(self, titulo, mensaje):
        ventana = customtkinter.CTkToplevel(self)
        ventana.geometry("300x150")
        ventana.title(titulo)
        ventana.configure(fg_color="#222222")
        etiqueta = customtkinter.CTkLabel(ventana, text=mensaje, text_color="white")
        etiqueta.pack(pady=20)
        boton = customtkinter.CTkButton(ventana, text="OK", command=lambda: self.cerrar_messagebox(ventana), fg_color="#4c607c")
        boton.pack(pady=10)
        ventana.grab_set()
        ventana.overrideredirect(True)

    def generar_pdf(self):
        self.hacer_zoom()
        try:
            # Solicitar ubicación para guardar el archivo
            from tkinter import filedialog
            pdf_path = filedialog.asksaveasfilename(
                parent=self,
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                title="Guardar estudio como PDF",
                initialfile="estudio_estaciones.pdf"
            )
            
            if not pdf_path:  # Si el usuario cancela
                return

            # Configurar tamaños de página (ambas en landscape)
            from reportlab.lib.pagesizes import letter, landscape
            width, height = landscape(letter)
            
            # Crear el PDF (todas las páginas en landscape)
            c = canvas.Canvas(pdf_path, pagesize=landscape(letter))
            
            # --- PRIMERA PÁGINA (MAPA) ---
            # Título más compacto
            titulo = "Factibilidad de Instalación de Nuevos Servicios"
            c.setFont("Helvetica-Bold", 16)
            ancho_texto = c.stringWidth(titulo, "Helvetica-Bold", 16)
            x_centrado = (width - ancho_texto) / 2
            c.drawString(x_centrado, height - 30, titulo)  # Reducido margen superior
            
            # Capturar el mapa
            x1 = self.mapa.winfo_rootx()
            y1 = self.mapa.winfo_rooty()
            x2 = x1 + self.mapa.winfo_width()
            y2 = y1 + self.mapa.winfo_height()
            
            map_image = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            map_image_path = os.path.join(tempfile.gettempdir(), "mapa_temp.png")
            map_image.save(map_image_path, quality=95)
            
            if os.path.exists(map_image_path):
                img = PILImage.open(map_image_path)
                img_width, img_height = img.size
                aspect = img_height / float(img_width)
                
                # Ajustar tamaño para ocupar casi toda la página
                new_width = width - 40  # Margen lateral reducido
                new_height = new_width * aspect
                
                # Posición Y ajustada para ocupar más espacio
                y_pos = height - new_height - 80  # Margen superior reducido
                
                c.drawImage(map_image_path, 20, y_pos,  # Margen izquierdo de 20 puntos
                        width=new_width, height=new_height)
                
                # Etiqueta pequeña bajo el mapa
                c.setFont("Helvetica", 8)
                c.drawString(20, y_pos - 15, "Mapa de estaciones con el sitio propuesto")
                c.drawString(20, y_pos - 25, self.label_info.cget("text").strip())
            
            # --- SEGUNDA PÁGINA (TABLA) ---
            c.showPage()
            
            # Preparar datos para la tabla
            headers = ["Nombre", "Latitud", "Longitud", "Altura", "Estado", "Distancia (km)"]
            data = [headers]
            
            for child in self.tabla_estaciones.get_children():
                data.append(self.tabla_estaciones.item(child)['values'])
            
            # Calcular anchos de columnas dinámicamente
            from reportlab.lib import units
            ancho_total = width - 40  # Margen izquierdo y derecho de 20 puntos
            
            # Ajustar ancho de la primera columna (Nombre) al máximo posible
            ancho_nombre = ancho_total * 0.40  # 40% del ancho total
            otros_anchos = [
                ancho_total * 0.12,  # Latitud
                ancho_total * 0.12,  # Longitud
                ancho_total * 0.10,  # Altura
                ancho_total * 0.16,  # Estado
                ancho_total * 0.10   # Distancia
            ]
            
            # Crear tabla con anchos ajustados
            from reportlab.platypus import Table, TableStyle
            from reportlab.lib import colors
            
            table = Table(data, 
                        colWidths=[ancho_nombre] + otros_anchos,
                        rowHeights=20)  # Altura de fila fija
            
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 10),
                ('FONTSIZE', (0,1), (-1,-1), 8),  # Tamaño más pequeño para datos
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('WORDWRAP', (0,0), (-1,-1)),  # Permitir ajuste de texto
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE')  # Centrado vertical
            ]))
            
            # Posicionar tabla centrada verticalmente
            table.wrapOn(c, width, height)
            table.drawOn(c, 20, (height - table._height) / 1.2)  # Centrado vertical
            
            # Metadatos
            c.setAuthor("FINS - Sistema de Factibilidad")
            c.setTitle("Factibilidad de Instalación de Nuevos Servicios)")
            c.setSubject(f"Estaciones en un rango de {self.rango.get()} km del sitio propuesto")
            c.save()
            
            # Mostrar mensaje
            self.mostrar_messagebox_oscuro("Éxito", 
                f"PDF guardado correctamente en:\n{pdf_path}\n\n"
                f"Estaciones en rango: {len(data)-1}")
            
        except Exception as e:
            self.mostrar_messagebox_oscuro("Error", 
                f"No se pudo generar el PDF:\n{str(e)}")

    def crear_mapa_inicial(self):
        """Crea el mapa centrado en Venezuela al iniciar el módulo"""
        # Limpiar widgets existentes en el frame derecho
        for widget in self.frame_derecho.winfo_children():
            widget.destroy()

        # Frame superior para la barra de búsqueda
        self.frame_busqueda = customtkinter.CTkFrame(self.frame_derecho, height=40, fg_color="transparent")
        self.frame_busqueda.pack(side="top", fill="x", padx=5, pady=5)

        # Barra de búsqueda
        self.busqueda_entry = customtkinter.CTkEntry(
            self.frame_busqueda, 
            placeholder_text="Buscar localidad...",
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

        # Frame contenedor principal (usará grid para distribución 90/10)
        self.frame_contenedor = customtkinter.CTkFrame(self.frame_derecho, fg_color="transparent")
        self.frame_contenedor.pack(fill="both", expand=True)

        # Configurar pesos para la distribución 90/10
        self.frame_contenedor.grid_rowconfigure(0, weight=9)  # 90% para el mapa
        self.frame_contenedor.grid_rowconfigure(1, weight=1)  # 10% para la tabla
        self.frame_contenedor.grid_columnconfigure(0, weight=1)

        # Frame del Mapa (90% del espacio)
        self.frame_mapa = customtkinter.CTkFrame(self.frame_contenedor)
        self.frame_mapa.grid(row=0, column=0, sticky="nsew", pady=(0, 2))

        # Configurar el mapa
        self.mapa = tkintermapview.TkinterMapView(self.frame_mapa, corner_radius=0)
        self.mapa.pack(fill="both", expand=True)

        # Centrar el mapa en Venezuela
        self.mapa.set_position(8.0, -66.0)  # Coordenadas aproximadas de Venezuela
        self.mapa.set_zoom(6)

        # Configurar evento para copiar coordenadas
        self.mapa.add_right_click_menu_command(
            label="Copiar coordenadas",
            command=self.copiar_coordenadas_click,
            pass_coords=True
        )

        # Frame de la Tabla (10% del espacio)
        self.frame_tabla = customtkinter.CTkFrame(self.frame_contenedor)
        self.frame_tabla.grid(row=1, column=0, sticky="nsew", pady=(2, 0))

        # Crear la tabla de estaciones
        self.crear_tabla_estaciones()

    def crear_tabla_estaciones(self):
        """Crea la tabla para mostrar las estaciones encontradas con contenido centrado"""
        # Estilo para la tabla
        style = ttk.Style()
        style.theme_use("default")
        
        # Configurar estilo para las celdas
        style.configure("Treeview",
            background=color_fondo2,
            foreground="#000000",
            rowheight=25,
            fieldbackground=color_fondo2,
            bordercolor="#343638",
            borderwidth=0,
            anchor="center",
            font=('Arial', 10))
            
        style.map('Treeview', background=[('selected', '#22559b')])
        
        # Configurar estilo para los encabezados
        style.configure("Treeview.Heading",
            background="#ffffff",
            foreground="#000000",
            relief="flat",
            anchor="center",
            font=('Arial', 10, 'bold'))
            
        style.map("Treeview.Heading",
            background=[('active', '#3484F0')])

        # Definición de columnas
        columnas = [
            ("nombre", "Nombre Estación", 200),
            ("latitud", "Latitud", 100),
            ("longitud", "Longitud", 100),
            ("altura", "Altura Torre", 100),
            ("estado", "Estado", 150),
            ("distancia", "Distancia", 100)
        ]
        
        # Crear Treeview con altura ajustada
        self.tabla_estaciones = ttk.Treeview(
            self.frame_tabla,
            columns=[col[0] for col in columnas],
            show="headings",
            selectmode="browse",
            height=4,  # Muestra 4 filas por defecto
            
        )
        
        # Configurar encabezados y columnas
        for col_name, heading_text, width in columnas:
            self.tabla_estaciones.heading(col_name, text=heading_text, anchor="center")
            self.tabla_estaciones.column(col_name, width=width, anchor="center")

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(
            self.frame_tabla,
            orient="vertical",
            command=self.tabla_estaciones.yview
        )
        self.tabla_estaciones.configure(yscrollcommand=scrollbar.set)

        # Empaquetar
        self.tabla_estaciones.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def buscar_localidad(self, event=None):
        """Busca una localidad usando geopy como alternativa"""
        localidad = self.busqueda_entry.get().strip()
        if localidad:
            try:
                geolocator = Nominatim(user_agent="fins_app")
                location = geolocator.geocode(localidad + ", Venezuela")
                
                if location:
                    lat, lon = location.latitude, location.longitude
                    # Centramos el mapa
                    self.mapa.set_position(lat, lon)
                    self.mapa.set_zoom(15)
                    
                    # Marcador sin texto
                    if hasattr(self, 'marcador_busqueda'):
                        self.mapa.delete(self.marcador_busqueda)
                    self.marcador_busqueda = self.mapa.set_marker(lat, lon, text="")  # Texto vacío
                    
                    # Actualizamos campos
                    self.punto_propuesto.delete(0, "end")
                    self.punto_propuesto.insert(0, f"{lat:.6f}, {lon:.6f}")
                    self.mostrar_mensaje_copiado(f"Localidad encontrada: {localidad}")
                else:
                    self.mostrar_messagebox_oscuro("Error", "Localidad no encontrada")
            except Exception as e:
                self.mostrar_messagebox_oscuro("Error", f"Error de conexión: {str(e)}")

    def actualizar_tabla_estaciones(self, estaciones):
        """Actualiza la tabla con las estaciones encontradas"""
        # Limpiar tabla existente
        for item in self.tabla_estaciones.get_children():
            self.tabla_estaciones.delete(item)
        
        # Insertar nuevas estaciones
        for estacion in estaciones:
            self.tabla_estaciones.insert("", "end", values=estacion)

    def copiar_coordenadas_click(self, coords):
        """Maneja el clic derecho para copiar coordenadas y actualizar el campo"""
        lat, lon = coords
        texto_coords = f"{lat:.6f}, {lon:.6f}"
        
        # Copiar al portapapeles
        self.clipboard_clear()
        self.clipboard_append(texto_coords)
        
        # Actualizar el campo de sitio propuesto
        self.punto_propuesto.delete(0, "end")
        self.punto_propuesto.insert(0, texto_coords)
        
        # Mostrar mensaje de confirmación
        self.mostrar_mensaje_copiado(f"Coordenadas copiadas: {texto_coords}")

    def mostrar_mensaje_copiado(self, mensaje):
        """Muestra un mensaje temporal"""
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

    def mantener_foco(self, event: Event = None):
        """Mantiene el foco en el campo de coordenadas"""
        if not self.punto_propuesto.get().strip():
            self.punto_propuesto.focus_set()

    def cerrar_messagebox(self, ventana):
        ventana.destroy()
        self.focus_force()

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
        
        

    def hacer_estudio(self):
        punto_texto = self.punto_propuesto.get().strip()
        rango_texto = self.rango.get().strip()

        self.boton3.configure(state="normal")

        # Validar coordenada
        try:
            punto_texto = punto_texto.replace(',', ' ')
            latitud, longitud = map(float, punto_texto.split())
        except:
            self.mostrar_messagebox_oscuro("ERROR", "Coordenadas inválidas.\nFormato esperado:\n99.99999 -99.9999\no\n99.99999,-99.9999")
            return

        # Validar rango
        try:
            rango_km = float(rango_texto) if rango_texto else 5.0  # Default 5 km
        except:
            self.mostrar_messagebox_oscuro("ERROR", "Rango inválido. Ingresa un número.")
            return

        # Limpiar todos los marcadores existentes
        self.mapa.delete_all_marker()
        
        # Eliminar label_info anterior si existe
        if hasattr(self, 'label_info'):
            self.label_info.destroy()
        
        # Pintar nuevo marcador del punto propuesto
        self.mapa.set_marker(latitud, longitud, text="Punto Propuesto", 
                            marker_color_circle="blue", 
                            marker_color_outside="blue")

        # Obtener todas las estaciones de la BD
        estaciones = obtener_todas()

        # Filtrar por distancia y preparar datos para la tabla
        estaciones_cercanas = []
        datos_tabla = []
        
        # Listas para calcular los límites del zoom
        lats = [latitud]
        lons = [longitud]
        
        for estacion in estaciones:
            _, nombre, lat_est, lon_est, altura, estado, *_ = estacion
            if lat_est is None or lon_est is None:
                continue
                
            # Calcular distancia
            distancia = geodesic((latitud, longitud), (lat_est, lon_est)).kilometers
            
            if distancia <= rango_km:
                estaciones_cercanas.append((nombre, lat_est, lon_est, distancia))
                datos_tabla.append((
                    nombre,
                    f"{lat_est:.6f}",
                    f"{lon_est:.6f}",
                    f"{altura} m" if altura else "N/A",
                    estado if estado else "N/A",
                    distancia
                ))
                # Agregar coordenadas para cálculo de zoom
                lats.append(lat_est)
                lons.append(lon_est)

        # Ordenar por distancia (de menor a mayor)
        datos_tabla_ordenados = sorted(datos_tabla, key=lambda x: x[5])
        
        # Convertir distancia a formato string después de ordenar
        datos_tabla_final = []
        for dato in datos_tabla_ordenados:
            datos_tabla_final.append((
                dato[0],  # nombre
                dato[1],  # latitud
                dato[2],  # longitud
                dato[3],  # altura
                dato[4],  # estado
                f"{dato[5]:.2f} km"  # distancia formateada
            ))

        # Pintar marcadores de estaciones cercanas (también ordenados)
        estaciones_cercanas_ordenadas = sorted(estaciones_cercanas, key=lambda x: x[3])
        for nombre, lat_est, lon_est, _ in estaciones_cercanas_ordenadas:
            self.mapa.set_marker(lat_est, lon_est, text=nombre, 
                            marker_color_circle="green", 
                            marker_color_outside="green")

        # --- NUEVO: Cálculo del zoom automático ---
        if estaciones_cercanas:
            # Calcular límites geográficos
            min_lat = min(lats)
            max_lat = max(lats)
            min_lon = min(lons)
            max_lon = max(lons)
            
            # Calcular centro del área
            center_lat = (min_lat + max_lat) / 2
            center_lon = (min_lon + max_lon) / 2
            
            # Calcular distancia diagonal para determinar el zoom
            diagonal_distance = geodesic((min_lat, min_lon), (max_lat, max_lon)).km
            
            # Ajustar el zoom basado en la distancia diagonal
            if diagonal_distance < 1:  # Menos de 1 km
                zoom_level = 15
            elif diagonal_distance < 5:  # Menos de 5 km
                zoom_level = 14
            elif diagonal_distance < 10:  # Menos de 10 km
                zoom_level = 13
            elif diagonal_distance < 20:  # Menos de 20 km
                zoom_level = 12
            elif diagonal_distance < 50:  # Menos de 50 km
                zoom_level = 11
            else:
                zoom_level = 10
            
            # Centrar y hacer zoom
            self.mapa.set_position(center_lat, center_lon)
            self.mapa.set_zoom(zoom_level)
        else:
            # Si no hay estaciones cercanas, centrar en el punto propuesto
            self.mapa.set_position(latitud, longitud)
            self.mapa.set_zoom(15)

        # Actualizar tabla con los datos ordenados
        self.actualizar_tabla_estaciones(datos_tabla_final)

        # Mostrar cantidad de estaciones cercanas
        self.label_info = customtkinter.CTkLabel(
            self.mapa,
            text=f" Estaciones en el rango de {rango_km} Kms: ({len(estaciones_cercanas)}) ",
            font=("Arial", 14, "bold"),
            fg_color=color_fondo3,
            text_color="#ffffff",
            corner_radius=10,
            padx=10         
        )
        self.label_info.place(relx=0.5, rely=0.02, anchor="n")
        
        # Eliminar la referencia al marcador de búsqueda anterior
        if hasattr(self, 'marcador_busqueda'):
            del self.marcador_busqueda

    def limpiar_campos(self):
        self.boton3.configure(state="disabled")


        # Limpiar campos de entrada
        self.punto_propuesto.delete(0, "end")
        self.rango.delete(0, "end")
        self.busqueda_entry.delete(0, "end")
         
        # Limpiar tabla de resultados
        for item in self.tabla_estaciones.get_children():
            self.tabla_estaciones.delete(item)
        
        # Limpiar todos los marcadores del mapa
        self.mapa.delete_all_marker()
        
        # Eliminar label_info si existe
        if hasattr(self, 'label_info'):
            self.label_info.destroy()
            del self.label_info
        
        # Eliminar referencia al marcador de búsqueda si existe
        if hasattr(self, 'marcador_busqueda'):
            del self.marcador_busqueda
        
        # Centrar el mapa en Venezuela nuevamente
        self.mapa.set_position(8.0, -66.0)  # Coordenadas de Venezuela
        self.mapa.set_zoom(6)

    def cerrar_modulo(self):
        self.destroy()
        if self.master is not None:
            self.master.deiconify()
            self.master.focus_force()