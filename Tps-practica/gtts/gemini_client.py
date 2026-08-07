"""Cliente simple para la API gratuita de Gemini."""

import os
import re

from google import genai
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

MODELO_GEMINI = "gemini-flash-latest"

_api_key = os.getenv("GEMINI_API_KEY")
if not _api_key:
    raise RuntimeError("Falta GEMINI_API_KEY en el archivo .env de la raíz del proyecto.")

_client = genai.Client(api_key=_api_key)


def _limpiar_markdown(texto):
    texto = re.sub(r"\*\*(.*?)\*\*", r"\1", texto)  # **negrita**
    texto = re.sub(r"\*(.*?)\*", r"\1", texto)  # *cursiva*
    texto = re.sub(r"`(.*?)`", r"\1", texto)  # `código`
    texto = re.sub(r"^#+\s*", "", texto, flags=re.MULTILINE)  # # títulos
    texto = re.sub(r"^[-•]\s*", "", texto, flags=re.MULTILINE)  # - viñetas
    return texto


def preguntar_gemini(pregunta):
    respuesta = _client.models.generate_content(model=MODELO_GEMINI, contents=pregunta)
    return _limpiar_markdown(respuesta.text.strip())
