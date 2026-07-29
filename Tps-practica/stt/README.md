# Transcriptor de notas/reuniones

App Flask que transcribe audio a texto usando `faster-whisper`
(corre 100% local, sin internet, sin límites de uso) y guarda
un historial de transcripciones en SQLite.

## Instalación

```bash
python3 -m venv venv
source venv/bin/activate        # en Windows: venv\Scripts\activate

pip install -r requirements.txt
```

**Nota sobre `pyaudio`/audio:** para este proyecto NO hace falta
`pyaudio` (eso era para el ejemplo con micrófono en vivo). Acá
solo se suben archivos de audio ya grabados.

## Cómo correrlo

```bash
python app.py
```

Abrí `http://127.0.0.1:5000` en el navegador.

La primera vez que subas un audio, `faster-whisper` va a
descargar el modelo "small" (~250 MB) automáticamente desde
Hugging Face. Después queda cacheado localmente y no se vuelve
a descargar.

## Estructura

```
transcriptor/
├── app.py              # rutas y lógica de Flask
├── database.py         # manejo de SQLite
├── requirements.txt
├── templates/
│   ├── base.html
│   ├── index.html       # historial de transcripciones
│   ├── subir.html        # formulario de subida
│   └── ver.html          # ver una transcripción
└── uploads/             # audios guardados (se crea solo)
```

## Cosas para mejorar (ideas para el TP)

- **Diarización de hablantes**: identificar "quién dijo qué" con
  `pyannote-audio` (útil si es una reunión con varias personas).
- **Resumen automático**: mandar el texto transcripto a un LLM
  para generar un resumen o lista de action items.
- **Exportar a PDF/Word**: descargar la transcripción como
  documento.
- **Progreso en tiempo real**: mostrar una barra de progreso
  mientras transcribe (con WebSockets o polling), ya que audios
  largos pueden tardar.
- **Cambiar el tamaño del modelo**: en `app.py`, línea de
  `WhisperModel("small", ...)` podés probar `"base"` (más rápido,
  menos preciso) o `"medium"`/`"large-v3"` (más preciso, más
  lento) según tu hardware.

## Nota sobre precisión vs velocidad

El modelo `small` es un buen punto de partida. Si tenés GPU
disponible, cambiá `device="cpu"` por `device="cuda"` en
`get_modelo()` — la transcripción va a ser mucho más rápida.
