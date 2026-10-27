"""Pruebas del flujo sin llamadas a proveedores externos."""

import json

from agents.competidores import CompetidoresAgent
from orchestrator import AGENT_IDS, Orchestrator


class FakeLLM:
    """LLM falso que responde con un resultado válido por agente."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        self.calls.append(user_prompt)
        if "competidores dinámicos" in system_prompt:
            result = {"summary_markdown": "competidores", "competitors": []}
        elif "posicionamiento observable" in system_prompt:
            result = {"summary_markdown": "posicionamiento", "competitors": []}
        elif "Compara la oferta" in system_prompt:
            result = {
                "summary_markdown": "comparación",
                "strengths": [],
                "overlaps": [],
                "weaknesses": [],
            }
        elif "Identifica segmentos" in system_prompt:
            result = {"summary_markdown": "segmentos", "segments": []}
        else:
            result = {
                "summary_markdown": "estratega",
                "recommended_niche": "sin evidencia suficiente",
                "positioning_statement": "sin evidencia suficiente",
                "strategic_hypothesis": "sin evidencia suficiente",
                "experiments": [
                    {"experiment": "Experimento de prueba 1", "success_metric": "métrica 1"},
                    {"experiment": "Experimento de prueba 2", "success_metric": "métrica 2"},
                    {"experiment": "Experimento de prueba 3", "success_metric": "métrica 3"},
                ],
                "main_risks": [],
            }
        return json.dumps(result, ensure_ascii=False)


class FakeSearch:
    def search(self, query: str, since_days: int = 180) -> list[dict[str, str]]:
        return []


class FabricatedCompetitorLLM:
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        return json.dumps(
            {
                "summary_markdown": "competidor inventado",
                "competitors": [
                    {
                        "name": "Empresa no respaldada",
                        "country": "Chile",
                        "growth_signals": ["Señal no respaldada"],
                        "dynamism": "alto",
                        "source_url": "https://example.invalid/fuente",
                        "source_date": "2026-10-25",
                    }
                ],
            }
        )


def test_run_all_executes_agents_in_order_and_passes_prior_results() -> None:
    llm = FakeLLM()
    progress: list[tuple[int, str]] = []
    orchestrator = Orchestrator(llm, FakeSearch())

    results = orchestrator.run_all(
        {"company": "Proyecto", "industry": "software", "region": "Chile"},
        lambda index, name: progress.append((index, name)),
    )

    assert tuple(results) == AGENT_IDS
    assert len(llm.calls) == 5
    assert [index for index, _ in progress] == [1, 2, 3, 4, 5]
    assert '"competidores"' in llm.calls[1]
    assert '"posicionamiento"' in llm.calls[2]
    assert '"segmentos"' in llm.calls[4]


def test_run_agent_can_run_one_agent_with_existing_context() -> None:
    llm = FakeLLM()
    orchestrator = Orchestrator(llm, FakeSearch())

    result = orchestrator.run_agent(
        2,
        {"company": "Proyecto"},
        {
            "competidores": {"competitors": []},
            "estratega": {"recommended_niche": "dato futuro"},
        },
    )

    assert result.summary_markdown == "comparación"
    assert len(llm.calls) == 1
    assert '"competidores"' in llm.calls[0]
    assert '"estratega"' not in llm.calls[0]


def test_competitor_agent_discards_unverified_sources() -> None:
    agent = CompetidoresAgent(FabricatedCompetitorLLM(), FakeSearch())

    result = agent.run({"company": "Proyecto", "industry": "software", "region": "Chile"})

    assert result.competitors == []
    assert "no se conservaron" in result.summary_markdown.lower()
