# Asistente de voz con palabra clave + Gemini

## Qué hace

Un asistente de voz que:

1. Escucha continuamente en tu micrófono y detecta la palabra clave **"asistente"** de forma 100% local (usando `faster-whisper`, sin tocar ningún servicio de Google para esto).
2. Cuando la detecta, grava tu pregunta (corta sola cuando dejás de hablar).
3. Transcribe la pregunta con Whisper y se la manda a **Gemini** (API gratuita de Google) para que la responda.
4. Lee la respuesta en voz alta con `gTTS`.

Después de responder, vuelve a esperar la palabra clave (loop continuo, hasta que lo cortes con `Ctrl+C`).

## Requisitos

- Python 3.12+
- Micrófono
- Una API key gratuita de Gemini: https://aistudio.google.com/app/apikey

## Instalación

1. Copiá el archivo de ejemplo de variables de entorno (está en la raíz del proyecto) y completá tu key:

   ```
   cp ../../.env.example ../../.env
   ```

   Y en `.env` completá:

   ```
   GEMINI_API_KEY=tu_key_acá
   ```

2. Instalá las dependencias:

   ```
   pip install -r requirements.txt
   ```

## Cómo correrlo

Desde esta carpeta (`Tps-practica/gtts`):

```
python main.py
```

Esperá el mensaje "Escuchando...", decí **"asistente"**, y cuando te lo indique hacé tu pregunta en voz alta.
