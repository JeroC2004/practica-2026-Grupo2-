"""
Transcriptor de notas/reuniones - App Flask
---------------------------------------------
Subís un archivo de audio, se transcribe con faster-whisper
(corre local, sin internet, sin límites de uso) y queda
guardado en un historial consultable.
"""
import os
import time
from flask import Flask, render_template, request, redirect, url_for, flash, abort

import database as db

UPLOAD_FOLDER = "uploads"
EXTENSIONES_PERMITIDAS = {"mp3", "wav", "m4a", "ogg", "flac", "mp4"}

app = Flask(__name__)
app.secret_key = "cambiar-esto-en-produccion"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024  # 200 MB máx

# El modelo se carga una sola vez (perezosamente, en el primer uso)
_modelo = None


def get_modelo():
    global _modelo
    if _modelo is None:
        from faster_whisper import WhisperModel
        # "small" es un buen balance velocidad/precisión para CPU.
        # Opciones: tiny, base, small, medium, large-v3
        _modelo = WhisperModel("small", device="cpu", compute_type="int8")
    return _modelo


def extension_permitida(nombre_archivo):
    return "." in nombre_archivo and \
        nombre_archivo.rsplit(".", 1)[1].lower() in EXTENSIONES_PERMITIDAS


@app.route("/")
def index():
    transcripciones = db.listar_transcripciones()
    return render_template("index.html", transcripciones=transcripciones)


@app.route("/subir", methods=["GET", "POST"])
def subir():
    if request.method == "GET":
        return render_template("subir.html")

    archivo = request.files.get("audio")
    titulo = request.form.get("titulo", "").strip()

    if not archivo or archivo.filename == "":
        flash("Tenés que seleccionar un archivo de audio.")
        return redirect(url_for("subir"))

    if not extension_permitida(archivo.filename):
        flash("Formato no soportado. Usá mp3, wav, m4a, ogg, flac o mp4.")
        return redirect(url_for("subir"))

    if not titulo:
        titulo = archivo.filename

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    nombre_guardado = f"{int(time.time())}_{archivo.filename}"
    ruta_guardado = os.path.join(app.config["UPLOAD_FOLDER"], nombre_guardado)
    archivo.save(ruta_guardado)

    try:
        modelo = get_modelo()
        segmentos, info = modelo.transcribe(ruta_guardado, language="es")
        texto_completo = " ".join(segmento.text.strip() for segmento in segmentos)
        duracion = info.duration
    except Exception as e:
        flash(f"Error al transcribir: {e}")
        return redirect(url_for("subir"))

    db.guardar_transcripcion(titulo, texto_completo, nombre_guardado, duracion)
    flash("¡Transcripción lista!")
    return redirect(url_for("index"))


@app.route("/transcripcion/<int:id_>")
def ver_transcripcion(id_):
    t = db.obtener_transcripcion(id_)
    if t is None:
        abort(404)
    return render_template("ver.html", t=t)


@app.route("/transcripcion/<int:id_>/eliminar", methods=["POST"])
def eliminar(id_):
    db.eliminar_transcripcion(id_)
    flash("Transcripción eliminada.")
    return redirect(url_for("index"))


if __name__ == "__main__":
    db.init_db()
    app.run(debug=True, port=5000)
