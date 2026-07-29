from flask import Flask, render_template, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

DATABASE = "estacionamiento.db"


def get_db():
    return sqlite3.connect(DATABASE)


def obtener_plazas():

    conexion = get_db()

    cursor = conexion.cursor()

    cursor.execute("""
    SELECT id, estado
    FROM plazas
    """)

    plazas = cursor.fetchall()

    conexion.close()

    return plazas


def obtener_plaza(id):

    conexion = get_db()

    cursor = conexion.cursor()

    cursor.execute("""
    SELECT id, estado
    FROM plazas
    WHERE id = ?
    """, (id,))

    plaza = cursor.fetchone()

    conexion.close()

    return plaza


def cambiar_estado(id, estado):

    conexion = get_db()

    cursor = conexion.cursor()

    cursor.execute("""
    UPDATE plazas
    SET estado = ?
    WHERE id = ?
    """, (estado, id))

    conexion.commit()
    conexion.close()


def registrar_historial(id_plaza, estado):

    conexion = get_db()

    cursor = conexion.cursor()

    fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    cursor.execute("""
    INSERT INTO historial(plaza_id, estado, fecha)
    VALUES (?, ?, ?)
    """, (id_plaza, estado, fecha))

    conexion.commit()
    conexion.close()


@app.route('/')
def inicio():
    return render_template('index.html')


@app.route('/plazas')
def mostrar_plazas():

    plazas = obtener_plazas()

    return render_template(
        'plazas.html',
        plazas=plazas
    )


@app.route('/plazas/<estado>')
def filtrar_plazas(estado):

    conexion = get_db()

    cursor = conexion.cursor()

    cursor.execute("""
    SELECT id, estado
    FROM plazas
    WHERE estado = ?
    """, (estado.capitalize(),))

    plazas = cursor.fetchall()

    conexion.close()

    return render_template(
        'plazas.html',
        plazas=plazas
    )


@app.route('/plaza/<int:id>')
def detalle_plaza(id):

    plaza = obtener_plaza(id)

    return render_template(
        'plaza.html',
        plaza=plaza
    )


@app.route('/plaza/<int:id>/reservar')
def reservar(id):

    cambiar_estado(id, "Reservada")

    registrar_historial(
        id,
        "Reservada"
    )

    return redirect(f'/plaza/{id}')


@app.route('/plaza/<int:id>/ocupar')
def ocupar(id):

    cambiar_estado(id, "Ocupada")

    registrar_historial(
        id,
        "Ocupada"
    )

    return redirect(f'/plaza/{id}')


@app.route('/plaza/<int:id>/liberar')
def liberar(id):

    cambiar_estado(id, "Libre")

    registrar_historial(
        id,
        "Libre"
    )

    return redirect(f'/plaza/{id}')


@app.route('/estadisticas')
def estadisticas():

    conexion = get_db()

    cursor = conexion.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM plazas
    WHERE estado='Libre'
    """)
    libres = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*)
    FROM plazas
    WHERE estado='Reservada'
    """)
    reservadas = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*)
    FROM plazas
    WHERE estado='Ocupada'
    """)
    ocupadas = cursor.fetchone()[0]

    conexion.close()

    total = libres + reservadas + ocupadas

    porcentaje = round(
        ((ocupadas + reservadas) / total) * 100,
        2
    )

    return render_template(
        'estadisticas.html',
        libres=libres,
        reservadas=reservadas,
        ocupadas=ocupadas,
        porcentaje=porcentaje
    )


@app.route('/historial')
def historial():

    conexion = get_db()

    cursor = conexion.cursor()

    cursor.execute("""
    SELECT plaza_id, estado, fecha
    FROM historial
    ORDER BY id DESC
    """)

    registros = cursor.fetchall()

    conexion.close()

    return render_template(
        'historial.html',
        registros=registros
    )


if __name__ == '__main__':
    app.run(debug=True)