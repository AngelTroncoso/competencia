"""Agente que formula una hipótesis estratégica comprobable."""

from agents.base import BaseAgent
from agents.models import StrategistResult


class EstrategaAgent(BaseAgent):
    name = "Estratega"
    result_model = StrategistResult
    instructions = """
Formula una recomendación estratégica específica usando únicamente evidencia del
contexto. No presentes conjeturas como hechos. Incluye nicho, declaración de
posicionamiento, hipótesis literal en formato «Creemos que [segmento] valorará
[promesa] porque [evidencia]», tres experimentos baratos con métrica de éxito y
riesgos principales. Si no hay evidencia suficiente, dilo explícitamente y diseña
experimentos para resolver la incertidumbre. Devuelve exclusivamente JSON válido con
summary_markdown, recommended_niche, positioning_statement, strategic_hypothesis,
experiments (experiment, success_metric) y main_risks.
"""
