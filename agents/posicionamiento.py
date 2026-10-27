"""Agente que analiza mensajes y posicionamiento competitivo."""

from agents.base import BaseAgent
from agents.models import PositioningResult


class PosicionamientoAgent(BaseAgent):
    name = "Posicionamiento"
    result_model = PositioningResult
    requires_search = True
    instructions = """
Analiza el posicionamiento observable de los competidores detectados por el agente
anterior. Usa las fuentes recientes proporcionadas y sus URLs/fechas; no agregues
hechos no respaldados. Resume promesa, audiencia, diferenciadores, tono y precio
percibido. El precio percibido solo puede inferirse de evidencia explícita; en otro
caso escribe «sin evidencia suficiente». Salida exclusivamente JSON válido con
summary_markdown y competitors (competitor_name, promise, audience, differentiators, message_tone, perceived_price,
source_url y source_date (YYYY-MM-DD exacto como aparece en web_sources). No inventes
URLs ni fechas.
"""

    def search_query(self, context: dict) -> str:
        names = [
            item.get("name", "")
            for item in context.get("results", {}).get("competidores", {}).get("competitors", [])
        ]
        if not names:
            names = context.get("known_competitors", [])
        return (
            f"posicionamiento promesa clientes propuesta de valor precio "
            f"{' '.join(names)} {context.get('industry', '')} "
            f"publicado últimos seis meses"
        )
