"""Interfaz Streamlit para el análisis estratégico multiagente."""

import os
from typing import Any

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from streamlit.errors import StreamlitSecretNotFoundError

from agents.models import (
    ComparisonResult,
    CompetitorsResult,
    PositioningResult,
    SegmentsResult,
    StrategistResult,
)
from llm import LLMClient, LLMError, Provider
from orchestrator import AGENT_IDS, Orchestrator
from tools.search import SearchError, WebSearch
from utils.report import build_report

load_dotenv()

st.set_page_config(page_title="Estrategia Competitiva Multiagente", page_icon=":material/insights:", layout="wide")
st.title("Estrategia Competitiva Multiagente")
st.write(
    "Cinco agentes analizan competidores, posicionamiento, brechas de mercado y "
    "una hipótesis estratégica comprobable. Las afirmaciones sin respaldo se "
    "marcan como «sin evidencia suficiente»."
)

PROVIDER_KEYS = {
    "Gemini": ("GEMINI_API_KEY", "GEMINI_API_KEY"),
    "OpenAI": ("OPENAI_API_KEY", "OPENAI_API_KEY"),
    "Anthropic": ("ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY"),
    "OpenRouter": ("OPENROUTER_API_KEY", "OPENROUTER_API_KEY"),
}
AGENT_LABELS = [
    "Agente 1: Competidores",
    "Agente 2: Posicionamiento",
    "Agente 3: Comparación",
    "Agente 4: Segmentos",
    "Agente 5: Estratega",
]


def _configured_key(secret_name: str) -> str:
    """Lee la clave desde Streamlit Secrets o el entorno."""
    try:
        secret = st.secrets.get(secret_name, "")
    except StreamlitSecretNotFoundError:
        secret = ""
    return str(secret or os.getenv(secret_name, "")).strip()


def _get_orchestrator(provider: Provider, api_key: str) -> Orchestrator:
    return Orchestrator(LLMClient(provider, api_key), WebSearch())


def _run_full_analysis(context: dict[str, Any], provider: Provider, api_key: str) -> None:
    progress = st.progress(0, text="Preparando análisis...")
    status = st.status("Iniciando la cadena de agentes...", expanded=True)

    def update_progress(index: int, agent_name: str) -> None:
        progress.progress((index - 1) / 5, text=f"Agente {index} de 5: {agent_name}...")
        status.update(label=f"Agente {index} de 5: {agent_name}...", state="running")

    try:
        results = _get_orchestrator(provider, api_key).run_all(context, update_progress)
        st.session_state.analysis_results = results
        progress.progress(1.0, text="Análisis completo")
        status.update(label="Los cinco agentes terminaron.", state="complete")
    except (LLMError, SearchError, ValueError, RuntimeError) as exc:
        status.update(label="El análisis no pudo completarse.", state="error")
        st.error(f"No se completó el análisis: {exc}")


def _demo_results() -> dict[str, Any]:
    """Crea resultados explícitamente ilustrativos para explorar la interfaz."""
    return {
        "competidores": CompetitorsResult(
            summary_markdown="**Modo demo:** registro ficticio de muestra. No representa una empresa ni un hallazgo real.",
            competitors=[
                {
                    "name": "Empresa de ejemplo ficticia",
                    "country": "Ejemplo sintético",
                    "growth_signals": ["Señal ilustrativa para probar la tabla"],
                    "dynamism": "medio",
                    "source_url": "sin evidencia suficiente",
                    "source_date": "sin evidencia suficiente",
                }
            ],
        ),
        "posicionamiento": PositioningResult(
            summary_markdown="**Modo demo:** ejemplo ficticio para probar la vista; no es posicionamiento verificado.",
            competitors=[
                {
                    "competitor_name": "Empresa de ejemplo ficticia",
                    "promise": "Promesa de muestra, no verificada",
                    "audience": "Audiencia de muestra",
                    "differentiators": ["Diferenciador ilustrativo"],
                    "message_tone": "Ejemplo",
                    "perceived_price": "sin evidencia suficiente",
                    "source_url": "sin evidencia suficiente",
                    "source_date": "sin evidencia suficiente",
                }
            ],
        ),
        "comparacion": ComparisonResult(
            summary_markdown="**Modo demo:** matriz de muestra sintética, no inferida de datos reales.",
            strengths=[{"point": "Ejemplo de fortaleza", "evidence": "Dato sintético de demostración."}],
            overlaps=[{"point": "Ejemplo de duplicación", "evidence": "Dato sintético de demostración."}],
            weaknesses=[{"point": "Ejemplo de debilidad", "evidence": "Dato sintético de demostración."}],
        ),
        "segmentos": SegmentsResult(
            summary_markdown="**Modo demo:** segmento sintético para probar la tabla; no se consultó demanda real.",
            segments=[
                {
                    "segment": "Segmento de ejemplo",
                    "estimated_size": "sin evidencia suficiente",
                    "demand_evidence": "Dato sintético de demostración, no es evidencia.",
                    "opportunity_level": "bajo",
                    "underserved_reason": "Ejemplo ilustrativo",
                    "source_url": "sin evidencia suficiente",
                    "source_date": "sin evidencia suficiente",
                }
            ],
        ),
        "estratega": StrategistResult(
            summary_markdown="**Modo demo:** una recomendación real requiere evidencia y datos de tu negocio.",
            recommended_niche="sin evidencia suficiente",
            positioning_statement="sin evidencia suficiente",
            strategic_hypothesis="sin evidencia suficiente",
            experiments=[
                {"experiment": "Entrevistas sintéticas", "success_metric": "Métrica sintética"},
                {"experiment": "Página de prueba ficticia", "success_metric": "Métrica sintética"},
                {"experiment": "Oferta piloto ilustrativa", "success_metric": "Métrica sintética"},
            ],
            main_risks=["La demostración no consulta fuentes ni valida demanda."],
        ),
    }


def _agent_records(result: Any) -> list[dict[str, Any]]:
    if isinstance(result, CompetitorsResult):
        return [item.model_dump() for item in result.competitors]
    if isinstance(result, PositioningResult):
        return [item.model_dump() for item in result.competitors]
    if isinstance(result, ComparisonResult):
        return [
            {"tipo": category, **item.model_dump()}
            for category, values in (
                ("Fortaleza", result.strengths),
                ("Duplicación", result.overlaps),
                ("Debilidad", result.weaknesses),
            )
            for item in values
        ]
    if isinstance(result, SegmentsResult):
        return [item.model_dump() for item in result.segments]
    if isinstance(result, StrategistResult):
        records: list[dict[str, Any]] = [
            {
                "nicho recomendado": result.recommended_niche,
                "declaración de posicionamiento": result.positioning_statement,
                "hipótesis": result.strategic_hypothesis,
                "riesgos": "; ".join(result.main_risks) or "sin evidencia suficiente",
            }
        ]
        records.extend(
            {"experimento": item.experiment, "métrica de éxito": item.success_metric}
            for item in result.experiments
        )
        return records
    return []


def _render_agent(agent_id: str, result: Any) -> None:
    st.markdown(result.summary_markdown)
    records = _agent_records(result)
    st.subheader("Datos estructurados y fuentes")
    if records:
        st.dataframe(pd.DataFrame(records), width="stretch", hide_index=True)
    else:
        st.info("No se encontraron elementos con evidencia suficiente.")


if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = {}
if "analysis_context" not in st.session_state:
    st.session_state.analysis_context = {}
if "demo_mode" not in st.session_state:
    st.session_state.demo_mode = False

with st.sidebar:
    st.header("Datos del análisis")
    with st.form("analysis_form"):
        company = st.text_input("Nombre de mi empresa o proyecto")
        offer = st.text_area(
            "Oferta y posicionamiento actual",
            placeholder="Promesa, audiencia y diferenciadores",
            height=120,
        )
        industry = st.text_input("Nicho o industria")
        region = st.text_input("Región principal", value="Chile")
        international = st.checkbox("Incluir mercados internacionales")
        known_competitors = st.text_input("Competidores que ya conozco (opcional)")
        provider = st.selectbox(
            "Proveedor de IA",
            ["Gemini", "OpenAI", "Anthropic", "OpenRouter"],
            key="provider_input",
        )
        api_key = st.text_input(
            f"Clave API de {provider}",
            type="password",
            key="api_key_input",
            help="Opcional si ya configuraste la clave en Secrets o en variables de entorno.",
        )
        demo_mode = st.checkbox("Modo demo (sin clave API)")
        submit = st.form_submit_button("Ejecutar análisis completo", type="primary", width="stretch")

    if submit:
        missing = [
            label
            for label, value in (
                ("nombre de empresa/proyecto", company),
                ("descripción de la oferta", offer),
                ("nicho o industria", industry),
                ("región", region),
            )
            if not value.strip()
        ]
        effective_key = api_key.strip() or _configured_key(PROVIDER_KEYS[provider][0])
        if missing:
            st.error("Completa los campos obligatorios: " + ", ".join(missing) + ".")
        elif not demo_mode and not effective_key:
            st.error(
                f"Falta la clave de {provider}. Pégala aquí o configúrala en Secrets/entorno, "
                "o activa el modo demo."
            )
        else:
            context = {
                "company": company.strip(),
                "offer": offer.strip(),
                "industry": industry.strip(),
                "region": region.strip(),
                "international": international,
                "known_competitors": [
                    item.strip() for item in known_competitors.split(",") if item.strip()
                ],
            }
            st.session_state.analysis_context = context
            st.session_state.analysis_provider = provider
            st.session_state.analysis_results = {}
            st.session_state.demo_mode = demo_mode
            if demo_mode:
                st.session_state.analysis_results = _demo_results()
                st.success("Análisis de demostración listo. Los datos son ilustrativos, no hallazgos reales.")
            else:
                _run_full_analysis(context, provider, effective_key)


results = st.session_state.analysis_results
context = st.session_state.analysis_context
if results:
    if st.session_state.demo_mode:
        st.warning(
            "Modo demo: los ejemplos son sintéticos y solo sirven para probar la interfaz; "
            "no son hallazgos de mercado ni evidencia."
        )
    tabs = st.tabs(
        ["Competidores", "Posicionamiento", "Comparación", "Segmentos", "Estratega", "Informe completo"]
    )
    for index, agent_id in enumerate(AGENT_IDS):
        with tabs[index]:
            st.header(AGENT_LABELS[index])
            current_result = results.get(agent_id)
            if current_result is None:
                st.info("Este agente aún no se ha ejecutado. Ejecuta los agentes anteriores primero.")
            else:
                _render_agent(agent_id, current_result)
            dependencies_missing = [AGENT_IDS[prior] for prior in range(index) if AGENT_IDS[prior] not in results]
            rerun_disabled = bool(dependencies_missing) or st.session_state.demo_mode
            if dependencies_missing:
                st.caption("Primero ejecuta: " + ", ".join(dependencies_missing) + ".")
            if st.button(
                f"Volver a ejecutar Agente {index + 1}",
                key=f"rerun_{agent_id}",
                disabled=rerun_disabled,
            ):
                selected_provider = st.session_state.get("analysis_provider", "Gemini")
                selected_key = st.session_state.get("api_key_input", "") or _configured_key(
                    PROVIDER_KEYS[selected_provider][0]
                )
                if not selected_key:
                    st.error("Falta la clave API. Configúrala en la barra lateral o en Secrets.")
                else:
                    try:
                        updated = dict(results)
                        updated[agent_id] = _get_orchestrator(
                            selected_provider, selected_key
                        ).run_agent(index, context, results)
                        for downstream_id in AGENT_IDS[index + 1 :]:
                            updated.pop(downstream_id, None)
                        st.session_state.analysis_results = updated
                        st.rerun()
                    except (LLMError, SearchError, ValueError, RuntimeError) as exc:
                        st.error(f"No se pudo ejecutar el agente: {exc}")

    with tabs[-1]:
        st.header("Informe completo")
        report = build_report(context, results)
        st.markdown(report)
        st.download_button(
            "Descargar informe Markdown",
            data=report,
            file_name="estrategia-competitiva.md",
            mime="text/markdown",
            width="content",
        )
else:
    st.info("Completa los datos de la barra lateral y ejecuta el análisis o activa el modo demo.")
