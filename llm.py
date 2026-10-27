"""Capa única para acceder a modelos Gemini, OpenAI y Anthropic."""

import time
import os
from typing import Literal

Provider = Literal["Gemini", "OpenAI", "Anthropic", "OpenRouter"]


class LLMError(RuntimeError):
    """Error legible al comunicarse con el proveedor de IA."""


class LLMClient:
    """Cliente con reintentos limitados para una llamada de generación."""

    def __init__(self, provider: Provider, api_key: str, retries: int = 3) -> None:
        self.provider = provider
        self.api_key = api_key
        self.retries = retries

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        """Solicita una respuesta textual al proveedor configurado."""
        if not self.api_key.strip():
            raise LLMError(f"Falta la clave API de {self.provider}.")
        for attempt in range(self.retries):
            try:
                if self.provider == "OpenAI":
                    return self._openai(system_prompt, user_prompt)
                if self.provider == "OpenRouter":
                    return self._openrouter(system_prompt, user_prompt)
                if self.provider == "Anthropic":
                    return self._anthropic(system_prompt, user_prompt)
                return self._gemini(system_prompt, user_prompt)
            except LLMError:
                if attempt + 1 < self.retries:
                    time.sleep(2**attempt)
                else:
                    raise
        raise LLMError("No se pudo completar la solicitud.")

    def _openai(self, system_prompt: str, user_prompt: str) -> str:
        from openai import APIError, OpenAI

        try:
            response = OpenAI(api_key=self.api_key).chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.2,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
        except APIError as exc:
            self._raise_provider_error(exc)
        content = response.choices[0].message.content
        if not content:
            raise LLMError("El proveedor devolvió una respuesta vacía.")
        return content

    def _openrouter(self, system_prompt: str, user_prompt: str) -> str:
        from openai import APIError, OpenAI

        try:
            response = OpenAI(
                api_key=self.api_key,
                base_url="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": "http://localhost:8501",
                    "X-Title": "Estrategia Competitiva Multiagente",
                },
            ).chat.completions.create(
                model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
                temperature=0.2,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
        except APIError as exc:
            self._raise_provider_error(exc)
        content = response.choices[0].message.content
        if not content:
            raise LLMError("El proveedor devolvió una respuesta vacía.")
        return content

    def _anthropic(self, system_prompt: str, user_prompt: str) -> str:
        import anthropic

        try:
            response = anthropic.Anthropic(api_key=self.api_key).messages.create(
                model="claude-haiku-4-5",
                max_tokens=4000,
                temperature=0.2,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
        except anthropic.APIError as exc:
            self._raise_provider_error(exc)
        text_blocks = [block.text for block in response.content if hasattr(block, "text")]
        if not text_blocks:
            raise LLMError("El proveedor devolvió una respuesta vacía.")
        return "\n".join(text_blocks)

    def _gemini(self, system_prompt: str, user_prompt: str) -> str:
        from google import genai
        from google.genai.errors import APIError
        from google.genai import types

        try:
            response = genai.Client(api_key=self.api_key).models.generate_content(
                model="gemini-2.5-flash",
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    temperature=0.2,
                ),
            )
        except APIError as exc:
            self._raise_provider_error(exc)
        if not response.text:
            raise LLMError("El proveedor devolvió una respuesta vacía.")
        return response.text

    @staticmethod
    def _raise_provider_error(error: Exception) -> None:
        """Traduce errores conocidos del proveedor a mensajes accionables."""
        message = str(error)
        lowered = message.lower()
        if "rate" in lowered or "429" in lowered or "quota" in lowered:
            raise LLMError("El proveedor limitó el uso. Espera un momento o revisa tu cuota.") from error
        raise LLMError(f"Error del proveedor de IA: {message}") from error
