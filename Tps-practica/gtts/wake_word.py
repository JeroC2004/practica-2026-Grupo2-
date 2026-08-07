"""
Detección de palabra clave (wake word) 100% local, sin usar Google.

Graba audio en chunks cortos y usa faster-whisper (modelo "tiny") para
transcribirlos. Si el texto transcripto contiene la palabra clave, se
considera detectada.
"""

import tempfile
import wave

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

PALABRA_CLAVE = "asistente"
SAMPLERATE = 16000
DURACION_CHUNK = 2  # segundos por chunk de escucha
UMBRAL_ENERGIA = 300  # descarta chunks silenciosos antes de transcribir


def cargar_modelo_wake_word(nombre_modelo="tiny"):
    return WhisperModel(nombre_modelo, device="cpu", compute_type="int8")


def _grabar_chunk(duracion=DURACION_CHUNK, samplerate=SAMPLERATE):
    audio = sd.rec(int(duracion * samplerate), samplerate=samplerate, channels=1, dtype="int16")
    sd.wait()
    return audio


def _guardar_wav(audio, samplerate=SAMPLERATE):
    ruta_temp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
    with wave.open(ruta_temp, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(audio.tobytes())
    return ruta_temp


def _energia(audio):
    return np.abs(audio).mean()


def _tiene_energia(audio, umbral=UMBRAL_ENERGIA):
    return _energia(audio) > umbral


def escuchar_palabra_clave(modelo, palabra_clave=PALABRA_CLAVE):
    """Bloquea hasta detectar la palabra clave. Devuelve cuando la detecta."""
    print(f"\n👂 Escuchando... decí '{palabra_clave}' para activar el asistente.")
    while True:
        audio = _grabar_chunk()
        energia = _energia(audio)

        if energia <= UMBRAL_ENERGIA:
            continue

        ruta_audio = _guardar_wav(audio)
        segments, _ = modelo.transcribe(ruta_audio, language="es")
        texto = " ".join(seg.text.strip() for seg in segments).lower()

        if palabra_clave in texto:
            print(f"✅ Palabra clave detectada (\"{texto.strip()}\")")
            return
