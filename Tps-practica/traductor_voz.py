#!/usr/bin/env python3
"""
Traductor por voz
------------------
Graba audio desde el micrófono, lo transcribe con Whisper (faster-whisper),
lo traduce al idioma que elijas y te lo lee en voz alta con gTTS.

Uso básico:
    python traductor_voz.py --origen es --destino en --duracion 5

Uso interactivo (te avisa cuándo grabar y podés repetir):
    python traductor_voz.py --origen es --destino en --interactivo
"""

import argparse
import os
import tempfile
import wave

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from deep_translator import GoogleTranslator
from gtts import gTTS

try:
    from playsound import playsound
    TIENE_PLAYSOUND = True
except ImportError:
    TIENE_PLAYSOUND = False


# ---------------------------------------------------------------------------
# Grabación de audio
# ---------------------------------------------------------------------------
def grabar_audio(duracion=5, samplerate=16000):
    """Graba audio del micrófono durante 'duracion' segundos y devuelve la ruta
    a un archivo .wav temporal."""
    print(f"\n🎙️  Grabando {duracion} segundos... ¡hablá ahora!")
    audio = sd.rec(int(duracion * samplerate), samplerate=samplerate, channels=1, dtype="int16")
    sd.wait()
    print("✅ Grabación terminada.")

    ruta_temp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
    with wave.open(ruta_temp, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16 bits = 2 bytes
        wf.setframerate(samplerate)
        wf.writeframes(audio.tobytes())

    return ruta_temp


# ---------------------------------------------------------------------------
# Transcripción (Speech-to-Text) con Whisper
# ---------------------------------------------------------------------------
def transcribir_audio(modelo, ruta_audio, idioma_origen=None):
    """Transcribe el audio a texto usando faster-whisper."""
    segments, info = modelo.transcribe(ruta_audio, language=idioma_origen)
    texto = " ".join(seg.text.strip() for seg in segments)
    idioma_detectado = info.language
    return texto.strip(), idioma_detectado


# ---------------------------------------------------------------------------
# Traducción
# ---------------------------------------------------------------------------
def traducir_texto(texto, idioma_origen, idioma_destino):
    if not texto:
        return ""
    traductor = GoogleTranslator(source=idioma_origen, target=idioma_destino)
    return traductor.translate(texto)


# ---------------------------------------------------------------------------
# Texto a voz (Text-to-Speech)
# ---------------------------------------------------------------------------
def hablar_texto(texto, idioma, ruta_salida="traduccion.mp3"):
    if not texto:
        return None
    tts = gTTS(text=texto, lang=idioma)
    tts.save(ruta_salida)

    if TIENE_PLAYSOUND:
        try:
            playsound(ruta_salida)
        except Exception:
            print(f"(No se pudo reproducir automáticamente. Audio guardado en: {ruta_salida})")
    else:
        print(f"(Instalá 'playsound' para reproducción automática. Audio guardado en: {ruta_salida})")

    return ruta_salida


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Traductor de voz en tiempo real usando Whisper.")
    parser.add_argument("--origen", default="es", help="Idioma de origen (código, ej: es, en, pt). Default: es")
    parser.add_argument("--destino", default="en", help="Idioma de destino (código, ej: en, es, fr). Default: en")
    parser.add_argument("--duracion", type=int, default=5, help="Segundos a grabar por turno. Default: 5")
    parser.add_argument("--modelo", default="small",
                         choices=["tiny", "base", "small", "medium", "large-v3"],
                         help="Tamaño del modelo Whisper. Default: small")
    parser.add_argument("--interactivo", action="store_true",
                         help="Modo interactivo: presioná Enter para grabar cada vez, repite hasta que escribas 'salir'.")
    args = parser.parse_args()

    print("🔄 Cargando modelo Whisper... (la primera vez puede tardar, se descarga el modelo)")
    modelo = WhisperModel(args.modelo, device="cpu", compute_type="int8")
    print(f"✅ Modelo '{args.modelo}' listo.\n")
    print(f"Traduciendo de [{args.origen}] a [{args.destino}]")

    def ciclo_traduccion():
        ruta_audio = grabar_audio(duracion=args.duracion)
        texto_original, idioma_detectado = transcribir_audio(modelo, ruta_audio, idioma_origen=args.origen)
        os.remove(ruta_audio)

        if not texto_original:
            print("⚠️  No se detectó voz. Probá de nuevo.")
            return

        print(f"\n📝 Texto original ({idioma_detectado}): {texto_original}")

        traduccion = traducir_texto(texto_original, args.origen, args.destino)
        print(f"🌍 Traducción ({args.destino}): {traduccion}")

        hablar_texto(traduccion, args.destino)

    if args.interactivo:
        print("\nModo interactivo activado. Presioná ENTER para grabar, o escribí 'salir' para terminar.\n")
        while True:
            entrada = input("Presioná ENTER para grabar (o 'salir'): ")
            if entrada.strip().lower() == "salir":
                print("👋 ¡Listo, nos vemos!")
                break
            ciclo_traduccion()
    else:
        ciclo_traduccion()


if __name__ == "__main__":
    main()
