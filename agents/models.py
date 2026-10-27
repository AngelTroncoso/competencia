"""Esquemas Pydantic de entrada y salida de los agentes."""

from typing import Literal

from pydantic import BaseModel, Field


class AgentResult(BaseModel):
    """Resultado común con resumen en Markdown."""

    summary_markdown: str = Field(description="Resumen del análisis en español.")


class Competitor(BaseModel):
    """Competidor y señales verificables de actividad reciente."""

    name: str
    country: str = "sin evidencia suficiente"
    growth_signals: list[str] = Field(default_factory=list)
    dynamism: Literal["alto", "medio", "bajo"] = "bajo"
    source_url: str = "sin evidencia suficiente"
    source_date: str = "sin evidencia suficiente"


class CompetitorsResult(AgentResult):
    competitors: list[Competitor] = Field(default_factory=list)


class CompetitorPositioning(BaseModel):
    """Resumen del posicionamiento observado de una empresa."""

    competitor_name: str
    promise: str = "sin evidencia suficiente"
    audience: str = "sin evidencia suficiente"
    differentiators: list[str] = Field(default_factory=list)
    message_tone: str = "sin evidencia suficiente"
    perceived_price: str = "sin evidencia suficiente"
    source_url: str = "sin evidencia suficiente"
    source_date: str = "sin evidencia suficiente"


class PositioningResult(AgentResult):
    competitors: list[CompetitorPositioning] = Field(default_factory=list)


class ComparisonPoint(BaseModel):
    point: str
    evidence: str = "sin evidencia suficiente"


class ComparisonResult(AgentResult):
    strengths: list[ComparisonPoint] = Field(default_factory=list)
    overlaps: list[ComparisonPoint] = Field(default_factory=list)
    weaknesses: list[ComparisonPoint] = Field(default_factory=list)


class MarketSegment(BaseModel):
    segment: str
    estimated_size: str = "sin evidencia suficiente"
    demand_evidence: str = "sin evidencia suficiente"
    opportunity_level: Literal["alto", "medio", "bajo"] = "bajo"
    underserved_reason: str = "sin evidencia suficiente"
    source_url: str = "sin evidencia suficiente"
    source_date: str = "sin evidencia suficiente"


class SegmentsResult(AgentResult):
    segments: list[MarketSegment] = Field(default_factory=list)


class Experiment(BaseModel):
    experiment: str
    success_metric: str = "sin evidencia suficiente"


class StrategistResult(AgentResult):
    recommended_niche: str = "sin evidencia suficiente"
    positioning_statement: str = "sin evidencia suficiente"
    strategic_hypothesis: str = "sin evidencia suficiente"
    experiments: list[Experiment] = Field(min_length=3, max_length=3)
    main_risks: list[str] = Field(default_factory=list)
