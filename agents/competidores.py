"""Agente que encuentra competidores activos con fuentes recientes."""

from agents.base import BaseAgent
from agents.models import CompetitorsResult


class CompetidoresAgent(BaseAgent):
    name = "Competidores"
    result_model = CompetitorsResult
    requires_search = True
    instructions = """
Eres un analista de inteligencia competitiva. Identifica competidores dinámicos
en el nicho y región indicados, incluyendo mercados internacionales si se solicita.
Prioriza señales publicadas en los últimos seis meses desde la fecha actual:
lanzamientos, financiamiento, contrataciones, campañas y alianzas. Usa solo las
fuentes de web_sources entregadas. Descarta resultados sin fecha verificable o
anteriores al periodo. Incluye la fecha de publicación de cada fuente en formato YYYY-MM-DD, su URL exacta,
país y señales concretas. No inventes empresas, hechos, URLs, fechas ni cifras.
Si no hay fuentes suficientes, deja competidores vacío y explica la limitación.
El JSON debe tener exactamente: summary_markdown (string) y competitors (array de
objetos con name, country, growth_signals [strings], dynamism [alto|medio|bajo],
source_url y source_date).
"""

    def search_query(self, context: dict) -> str:
        region = context.get("region", "Chile")
        scope = "y mercados internacionales" if context.get("international") else ""
        known = ", ".join(context.get("known_competitors", []))
        return (
            f"empresas emergentes {context.get('industry', '')} en {region} {scope}; "
            f"crecimiento, lanzamientos, inversión, contrataciones, alianzas últimos 6 meses. "
            f"Competidores conocidos para ampliar búsqueda: {known}"
        )
