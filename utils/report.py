"""Generación del informe Markdown descargable."""

from typing import Any

from agents.models import AgentResult
from orchestrator import AGENT_IDS

AGENT_TITLES = {
    "competidores": "1. Competidores",
    "posicionamiento": "2. Posicionamiento",
    "comparacion": "3. Comparación",
    "segmentos": "4. Segmentos",
    "estratega": "5. Estratega",
}


def build_report(context: dict[str, Any], results: dict[str, AgentResult]) -> str:
    """Arma un reporte legible a partir de los datos validados."""
    lines = [
        "# Estrategia Competitiva Multiagente",
        "",
        f"**Empresa/proyecto:** {context.get('company', 'sin especificar')}",
        f"**Industria:** {context.get('industry', 'sin especificar')}",
        f"**Región:** {context.get('region', 'Chile')}",
        "",
        "> Los resultados dependen de la disponibilidad y calidad de las fuentes. "
        "Los elementos sin respaldo se indican como «sin evidencia suficiente».",
        "",
    ]
    for agent_id in AGENT_IDS:
        result = results.get(agent_id)
        if result is None:
            continue
        lines.extend([f"## {AGENT_TITLES[agent_id]}", "", result.summary_markdown, ""])
        if hasattr(result, "model_dump"):
            lines.extend(_format_details(agent_id, result.model_dump(mode="json")))
    return "\n".join(lines).strip() + "\n"


def _format_details(agent_id: str, data: dict[str, Any]) -> list[str]:
    excluded = {"summary_markdown"}
    lines: list[str] = []
    for key, value in data.items():
        if key in excluded or not value:
            continue
        label = key.replace("_", " ").capitalize()
        lines.append(f"### {label}")
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    description = item.get("name") or item.get("competitor_name") or item.get("segment") or item.get("point") or item.get("experiment") or ""
                    lines.append(f"- **{description}**")
                    for field, detail in item.items():
                        if field in {"name", "competitor_name", "segment", "point", "experiment"}:
                            continue
                        lines.append(f"  - {field.replace('_', ' ')}: {_display(detail)}")
                else:
                    lines.append(f"- {_display(item)}")
        else:
            lines.append(_display(value))
        lines.append("")
    return lines


def _display(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value)
