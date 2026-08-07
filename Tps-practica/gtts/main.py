"""
Asistente de voz: detecta la palabra clave localmente (sin Google),
y una vez activado, transcribe tu pregunta, se la manda a Gemini
y te lee la respuesta en voz alta.

Uso:
    python main.py
"""

import os
import tempfile
import wave

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from gtts import gTTS

from wake_word import cargar_modelo_wake_word, escuchar_palabra_clave, PALABRA_CLAVE, UMBRAL_ENERGIA
from gemini_client import preguntar_gemini

SAMPLERATE = 16000
DURACION_BLOQUE = 0.25  # segundos por bloque analizado
SILENCIO_PARA_CORTAR = 1.5  # segundos de silencio tras hablar para dar por terminada la pregunta
DURACION_MAXIMA_PREGUNTA = 15  # tope aunque sigas hablando


def grabar_pregunta(samplerate=SAMPLERATE):
    """Graba mientras haya voz y corta sola tras un silencio prolongado."""
    print("\n🎙️  Te escucho, hacé tu pregunta...")

    tam_bloque = int(DURACION_BLOQUE * samplerate)
    bloques = []
    tiempo_total = 0.0
    silencio_acumulado = 0.0
    empezo_a_hablar = False

    with sd.InputStream(samplerate=samplerate, channels=1, dtype="int16") as stream:
        while tiempo_total < DURACION_MAXIMA_PREGUNTA:
            bloque, _ = stream.read(tam_bloque)
            bloques.append(bloque.copy())
            tiempo_total += DURACION_BLOQUE

            energia = np.abs(bloque).mean()
            if energia > UMBRAL_ENERGIA:
                empezo_a_hablar = True
                silencio_acumulado = 0.0
            else:
                silencio_acumulado += DURACION_BLOQUE

            if empezo_a_hablar and silencio_acumulado >= SILENCIO_PARA_CORTAR:
                break

    print("✅ Grabación terminada.")
    audio = np.concatenate(bloques)

    ruta_temp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
    with wave.open(ruta_temp, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(audio.tobytes())
    return ruta_temp


def transcribir_pregunta(modelo, ruta_audio):
    segments, _ = modelo.transcribe(ruta_audio, language="es")
    return " ".join(seg.text.strip() for seg in segments).strip()


def hablar_respuesta(texto, idioma="es"):
    ruta_salida = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False).name
    tts = gTTS(text=texto, lang=idioma)
    tts.save(ruta_salida)

    try:
        os.startfile(ruta_salida)
    except OSError:
        print(f"(No se pudo reproducir automáticamente. Audio guardado en: {ruta_salida})")


def main():
    print("🔄 Cargando modelo Whisper (tiny) para detección de palabra clave...")
    modelo_wake_word = cargar_modelo_wake_word("tiny")

    print("🔄 Cargando modelo Whisper (small) para transcribir preguntas...")
    modelo_pregunta = WhisperModel("small", device="cpu", compute_type="int8")

    print(f"✅ Listo. Palabra clave: '{PALABRA_CLAVE}'. Ctrl+C para salir.\n")

    while True:
        try:
            escuchar_palabra_clave(modelo_wake_word)

            ruta_audio = grabar_pregunta()
            pregunta = transcribir_pregunta(modelo_pregunta, ruta_audio)
            os.remove(ruta_audio)

            if not pregunta:
                print("⚠️  No se detectó ninguna pregunta. Volviendo a escuchar la palabra clave.")
                continue

            print(f"📝 Pregunta: {pregunta}")

            print("🤔 Consultando a Gemini...")
            respuesta = preguntar_gemini(pregunta)
            print(f"💬 Respuesta: {respuesta}")

            hablar_respuesta(respuesta)

        except KeyboardInterrupt:
            print("\n👋 ¡Listo, nos vemos!")
            break


if __name__ == "__main__":
    main()
