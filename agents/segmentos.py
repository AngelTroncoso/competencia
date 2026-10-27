"""Agente que identifica segmentos con demanda y atención insuficiente."""

from agents.base import BaseAgent
from agents.models import SegmentsResult


class SegmentosAgent(BaseAgent):
    name = "Segmentos"
    result_model = SegmentsResult
    requires_search = True
    instructions = """
Identifica segmentos de mercado poco atendidos cuya demanda crece. Usa resultados
previos y las fuentes de búsqueda recientes; las fuentes deben tener fecha dentro de
los últimos seis meses. No inventes tamaño, crecimiento, cifras ni URLs. Usa
«sin evidencia suficiente» cuando no exista una fuente verificable. Devuelve
exclusivamente JSON válido con summary_markdown y segments: segment, estimated_size,
demand_evidence, opportunity_level (alto|medio|bajo), underserved_reason, source_url
y source_date (YYYY-MM-DD exacto de web_sources). Si no hay evidencia reciente,
devuelve lista vacía y explica por qué.
"""

    def search_query(self, context: dict) -> str:
        return (
            f"demanda creciente necesidades insatisfechas {context.get('industry', '')} "
            f"{context.get('region', 'Chile')} segmento mercado tendencias últimos seis meses"
        )
