"""Agente que compara la oferta del usuario con los competidores."""

from agents.base import BaseAgent
from agents.models import ComparisonResult


class ComparacionAgent(BaseAgent):
    name = "Comparación"
    result_model = ComparisonResult
    instructions = """
Compara la oferta y posicionamiento de la empresa con los resultados previos. Separa
fortalezas (donde supera), duplicaciones (donde se parece) y debilidades (donde queda
atrás). Cada punto debe incluir evidencia concreta citada desde el contexto. No
conviertas ausencia de información en una afirmación. Responde exclusivamente JSON
válido: summary_markdown y strengths, overlaps, weaknesses; cada lista contiene
objetos point y evidence. Usa «sin evidencia suficiente» si falta evidencia.
"""
