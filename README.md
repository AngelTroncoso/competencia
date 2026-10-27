# Estrategia Competitiva Multiagente

Aplicación Streamlit en español que coordina cinco agentes: competidores,
posicionamiento, comparación, segmentos desatendidos y recomendación estratégica.
Los agentes devuelven datos validados con Pydantic y un resumen Markdown. Los
hallazgos de mercado se limitan a fuentes fechadas dentro de los últimos seis meses;
si no se encuentra evidencia reciente, se indica explícitamente.

## Requisitos

- Python 3.11 o superior.
- Una clave de Gemini, OpenAI, Anthropic u OpenRouter para análisis reales.
- Tavily es opcional; sin `TAVILY_API_KEY` se intenta buscar con DuckDuckGo.

## Instalación y ejecución local

Desde la carpeta del proyecto, en PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run app.py
```

El proyecto requiere Python 3.11 o superior; ajusta `-3.12` a la versión instalada
si utilizas otra versión compatible.
También puedes utilizar el modo demo sin clave API; ese modo no presenta
competidores ni cifras ficticias como hallazgos reales.

Para configurar claves localmente, edita `.env` y añade la clave del proveedor
elegido. Si usas OpenRouter, puedes cambiar el modelo con `OPENROUTER_MODEL`.
Opcionalmente, copia `.streamlit/secrets.toml.example` a
`.streamlit/secrets.toml` e introduce allí tus claves. Ambos archivos reales están
excluidos de Git.

## Pruebas

```powershell
pytest -q
```

Las pruebas usan un LLM falso y no consumen créditos.

## Subir el proyecto a GitHub

1. Crea un repositorio vacío en GitHub. No subas `.env` ni
   `.streamlit/secrets.toml`.
2. Desde esta carpeta, inicializa Git y configura el repositorio remoto:

```powershell
git init
git add .
git commit -m "Crear Estrategia Competitiva Multiagente"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
git push -u origin main
```

Reemplaza la URL de ejemplo por la URL de tu repositorio. Si el repositorio ya
tiene un remoto configurado, no repitas `git remote add origin`.

## Desplegar en Streamlit Community Cloud

1. Publica el proyecto en GitHub siguiendo los pasos anteriores.
2. Abre [share.streamlit.io](https://share.streamlit.io) e inicia sesión con GitHub.
3. Pulsa **Create app**, selecciona el repositorio y la rama `main`.
4. En **Main file path**, escribe exactamente `app.py`.
5. Antes o después de crear la app, abre **Settings → Secrets** y pega las claves
   necesarias con formato TOML. Por ejemplo:

```toml
GEMINI_API_KEY = "tu-clave"
OPENAI_API_KEY = ""
ANTHROPIC_API_KEY = ""
OPENROUTER_API_KEY = ""
TAVILY_API_KEY = ""
```

6. Guarda los Secrets y espera a que Streamlit termine el despliegue. La clave de
   Tavily es opcional; la clave del proveedor elegido sí es necesaria para análisis
   reales. Puedes probar la interfaz sin claves usando el modo demo.

## Estructura

```text
app.py
agents/
  base.py
  models.py
  competidores.py
  posicionamiento.py
  comparacion.py
  segmentos.py
  estratega.py
tools/search.py
utils/report.py
orchestrator.py
llm.py
tests/test_orchestrator.py
requirements.txt
```
