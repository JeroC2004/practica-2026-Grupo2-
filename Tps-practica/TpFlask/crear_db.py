import sqlite3

conexion = sqlite3.connect("estacionamiento.db")
cursor = conexion.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS plazas(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    estado TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS historial(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plaza_id INTEGER,
    estado TEXT,
    fecha TEXT
)
""")

cursor.execute("SELECT COUNT(*) FROM plazas")
cantidad = cursor.fetchone()[0]

if cantidad == 0:
    for i in range(10):
        cursor.execute(
            "INSERT INTO plazas (estado) VALUES (?)",
            ("Libre",)
        )

conexion.commit()
conexion.close()

print("Base creada correctamente")