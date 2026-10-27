"""Orquestación secuencial de los cinco agentes."""

from collections.abc import Callable
from typing import Any

from agents.comparacion import ComparacionAgent
from agents.competidores import CompetidoresAgent
from agents.estratega import EstrategaAgent
from agents.posicionamiento import PosicionamientoAgent
from agents.segmentos import SegmentosAgent

AGENT_IDS = ("competidores", "posicionamiento", "comparacion", "segmentos", "estratega")


class Orchestrator:
    """Ejecuta agentes en orden y comparte los resultados anteriores."""

    def __init__(
        self,
        llm: Any,
        search_tool: Any | None = None,
        agents: list[Any] | None = None,
    ) -> None:
        self.agents = agents or [
            CompetidoresAgent(llm, search_tool),
            PosicionamientoAgent(llm, search_tool),
            ComparacionAgent(llm, search_tool),
            SegmentosAgent(llm, search_tool),
            EstrategaAgent(llm, search_tool),
        ]
        if len(self.agents) != len(AGENT_IDS):
            raise ValueError("El orquestador requiere exactamente cinco agentes.")

    def run_agent(
        self,
        index: int,
        user_context: dict[str, Any],
        results: dict[str, Any] | None = None,
    ) -> Any:
        """Ejecuta un solo agente con las salidas previas disponibles."""
        if not 0 <= index < len(self.agents):
            raise IndexError("Índice de agente fuera de rango.")
        context = dict(user_context)
        prior_results = {
            key: value
            for key, value in (results or {}).items()
            if key in AGENT_IDS[:index]
        }
        context["results"] = {
            key: value.model_dump(mode="json") if hasattr(value, "model_dump") else value
            for key, value in prior_results.items()
        }
        return self.agents[index].run(context)

    def run_all(
        self,
        user_context: dict[str, Any],
        progress_callback: Callable[[int, str], None] | None = None,
    ) -> dict[str, Any]:
        """Ejecuta la cadena de principio a fin e informa cada paso."""
        results: dict[str, Any] = {}
        for index, (agent_id, agent) in enumerate(zip(AGENT_IDS, self.agents), start=1):
            if progress_callback:
                progress_callback(index, agent.name)
            results[agent_id] = self.run_agent(index - 1, user_context, results)
        return results
