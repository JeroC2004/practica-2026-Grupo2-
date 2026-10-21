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


