"""Abstracción común para los agentes de análisis."""

import json
import re
from abc import ABC
from typing import Any, TypeVar

from pydantic import BaseModel

from agents.models import AgentResult

ResultT = TypeVar("ResultT", bound=AgentResult)


class BaseAgent(ABC):
    """Agente que convierte contexto y evidencia en un resultado validado."""

    name: str
    instructions: str
    result_model: type[ResultT]
    requires_search = False

    def __init__(self, llm: Any, search_tool: Any | None = None) -> None:
        self.llm = llm
        self.search_tool = search_tool

    def search_query(self, context: dict[str, Any]) -> str:
        """Construye una consulta de búsqueda en español."""
        company = context.get("company", "")
        industry = context.get("industry", "")
        region = context.get("region", "")
        return f"{industry} {region} competidores crecimiento lanzamientos inversión {company}"

    def run(self, context: dict[str, Any]) -> ResultT:
        """Ejecuta búsqueda opcional y valida la respuesta estructurada."""
        enriched_context = dict(context)
        if self.requires_search and self.search_tool is not None:
            enriched_context["web_sources"] = self.search_tool.search(
                self.search_query(context), since_days=180
            )
        prompt = (
            "Analiza el siguiente contexto. Responde únicamente con un objeto JSON "
            "válido que cumpla el esquema solicitado en tus instrucciones. "
            "Toda la salida debe estar en español. No inventes datos, fechas ni URLs; "
            "usa literalmente «sin evidencia suficiente» cuando corresponda.\n\n"
            f"Contexto:\n{json.dumps(enriched_context, ensure_ascii=False, default=self._json_default)}"
        )
        response = self.llm.complete(system_prompt=self.instructions, user_prompt=prompt)
        result = self.result_model.model_validate_json(self._extract_json(response))
        if self.requires_search:
            self._keep_only_cited_results(result, enriched_context.get("web_sources", []))
        return result

    @staticmethod
    def _json_default(value: Any) -> Any:
        if isinstance(value, BaseModel):
            return value.model_dump(mode="json")
        return str(value)

    @staticmethod
    def _extract_json(response: str) -> str:
        """Extrae JSON de la respuesta sin aceptar texto no estructurado."""
        text = response.strip()
        fenced = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
        if fenced:
            text = fenced.group(1).strip()
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end < start:
            raise ValueError("El modelo no devolvió un objeto JSON válido.")
        return text[start : end + 1]

    @staticmethod
    def _keep_only_cited_results(result: AgentResult, sources: list[dict[str, Any]]) -> None:
        """Descarta registros sin URL y fecha que coincidan con la búsqueda."""
        source_dates = {
            source["url"]: str(source["published_date"])[:10]
            for source in sources
            if source.get("url") and source.get("published_date")
        }
        field = "segments" if hasattr(result, "segments") else "competitors"
        records = getattr(result, field)
        verified = [
            item
            for item in records
            if item.source_url in source_dates
            and item.source_date[:10] == source_dates[item.source_url]
        ]
        if len(verified) != len(records):
            setattr(result, field, verified)
            if not verified:
                result.summary_markdown = (
                    "No se conservaron resultados porque las fuentes citadas no "
                    "coincidían exactamente con una URL y fecha verificadas dentro "
                    "del periodo consultado."
                )
            else:
                result.summary_markdown += (
                    "\n\nSe descartaron elementos cuyas fuentes no pudieron "
                    "verificarse contra los resultados de búsqueda."
                )
