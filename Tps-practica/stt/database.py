"""
Manejo de la base de datos SQLite para el transcriptor.
"""
import sqlite3
from datetime import datetime

DB_PATH = "transcripciones.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transcripciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            texto TEXT NOT NULL,
            nombre_archivo TEXT,
            duracion_seg REAL,
            fecha TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def guardar_transcripcion(titulo, texto, nombre_archivo, duracion_seg):
    conn = get_connection()
    conn.execute(
        """INSERT INTO transcripciones (titulo, texto, nombre_archivo, duracion_seg, fecha)
           VALUES (?, ?, ?, ?, ?)""",
        (titulo, texto, nombre_archivo, duracion_seg, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    conn.close()


def listar_transcripciones():
    conn = get_connection()
    filas = conn.execute(
        "SELECT id, titulo, nombre_archivo, duracion_seg, fecha FROM transcripciones ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return filas


def obtener_transcripcion(id_):
    conn = get_connection()
    fila = conn.execute(
        "SELECT * FROM transcripciones WHERE id = ?", (id_,)
    ).fetchone()
    conn.close()
    return fila


def eliminar_transcripcion(id_):
    conn = get_connection()
    conn.execute("DELETE FROM transcripciones WHERE id = ?", (id_,))
    conn.commit()
    conn.close()
