import sqlite3
import os
import sys
from pathlib import Path

def get_base_path():
    """Determina la ruta base correcta según el modo de ejecución"""
    if getattr(sys, 'frozen', False):
        # Modo compilado - recursos están junto al ejecutable
        return Path(sys.executable).parent
    # Modo desarrollo - raíz del proyecto (fuera de src/)
    return Path(__file__).parent.parent.parent

def get_resource_path(relative_path):
    """Obtiene la ruta absoluta correcta para cualquier recurso"""
    base_path = get_base_path()
    resource_path = base_path / relative_path
    # Crear directorios si no existen (solo para escritura)
    if any(part in relative_path for part in ['data', 'temp']):
        resource_path.parent.mkdir(parents=True, exist_ok=True)
    return str(resource_path)

# Rutas definitivas
DB_PATH = get_resource_path('data/fins.db')


def crear_tabla():
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_estacion TEXT,
            latitud REAL,
            longitud REAL,
            altura_torre REAL,
            estado TEXT,
            municipio TEXT,
            parroquia TEXT,
            tipo_estacion TEXT,
            observaciones TEXT
        )
    """)
    conn.commit()
    conn.close()

def insertar_estacion(datos):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO estaciones (
            nombre_estacion, latitud, longitud, altura_torre,
            estado, municipio, parroquia, tipo_estacion, observaciones
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, datos)
    conn.commit()
    conn.close()

def obtener_todas():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM estaciones")
    filas = cursor.fetchall()
    conn.close()
    return filas

def buscar_estacion(datos):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    nombre = datos[0]
    estado = datos[4]
    cursor.execute("""
        SELECT * FROM estaciones 
        WHERE nombre_estacion LIKE ? 
        AND estado LIKE ?
    """, (f'%{nombre}%', f'%{estado}%'))    
    filas = cursor.fetchall()
    conn.close()
    return filas

# def eliminar_estacion(id_):
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     cursor.execute("DELETE FROM estaciones WHERE id=?", (id_,))
#     conn.commit()
#     conn.close()



def actualizar_estacion(id_, datos):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE estaciones SET
            nombre_estacion=?, latitud=?, longitud=?, altura_torre=?,
            estado=?, municipio=?, parroquia=?, tipo_estacion=?, observaciones=?
        WHERE id=?
    """, (*datos, id_))
    conn.commit()
    conn.close()

def eliminar_estacion(id_):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM estaciones WHERE id=?", (id_,))
    conn.commit()
    conn.close()

def vaciar_tabla_estaciones():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM estaciones")  
        conn.commit()
    except Exception as e:
        print(f"Error al vaciar la tabla: {e}")
        raise
    finally:
        conn.close()

