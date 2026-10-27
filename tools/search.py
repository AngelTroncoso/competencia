"""Búsqueda web con Tavily y alternativa DuckDuckGo."""

import os
from datetime import date, datetime, timedelta, timezone
from typing import Any

import httpx
import requests
from duckduckgo_search.exceptions import DuckDuckGoSearchException
from tavily.errors import (
    BadRequestError,
    ForbiddenError,
    InvalidAPIKeyError,
    KeylessUnsupportedEndpointError,
    MissingAPIKeyError,
    TavilyKeylessLimitError,
    TimeoutError as TavilyTimeoutError,
    UsageLimitExceededError,
)


class SearchError(RuntimeError):
    """Error legible al consultar un proveedor de búsqueda."""


class WebSearch:
    """Busca páginas y conserva solo resultados con fecha reciente verificable."""

    def __init__(self) -> None:
        self.tavily_key = os.getenv("TAVILY_API_KEY", "").strip()

    def search(self, query: str, since_days: int = 180, max_results: int = 8) -> list[dict[str, str]]:
        """Devuelve resultados con URL, fecha, título y extracto."""
        cutoff = datetime.now(timezone.utc).date() - timedelta(days=since_days)
        try:
            if self.tavily_key:
                raw_results = self._tavily_search(query, max_results)
            else:
                raw_results = self._duckduckgo_search(query, max_results)
        except (
            DuckDuckGoSearchException,
            BadRequestError,
            ForbiddenError,
            InvalidAPIKeyError,
            KeylessUnsupportedEndpointError,
            MissingAPIKeyError,
            TavilyKeylessLimitError,
            TavilyTimeoutError,
            UsageLimitExceededError,
            httpx.HTTPError,
            requests.RequestException,
        ) as exc:
            raise SearchError(f"El servicio de búsqueda no respondió: {exc}") from exc
        results: list[dict[str, str]] = []
        for item in raw_results:
            published = self._as_date(
                item.get("published_date") or item.get("published") or item.get("date")
            )
            if not published or published < cutoff:
                continue
            url = str(item.get("url") or "").strip()
            if not url.startswith(("https://", "http://")):
                continue
            results.append(
                {
                    "title": str(item.get("title") or "Sin título"),
                    "url": url,
                    "published_date": published.isoformat(),
                    "content": str(item.get("content") or item.get("body") or "")[:2500],
                }
            )
        return results

    def _tavily_search(self, query: str, max_results: int) -> list[dict[str, Any]]:
        from tavily import TavilyClient

        response = TavilyClient(api_key=self.tavily_key).search(
            query=f"{query} after:{(date.today() - timedelta(days=180)).isoformat()}",
            search_depth="advanced",
            max_results=max_results,
            include_answer=False,
        )
        return response.get("results", [])

    @staticmethod
    def _duckduckgo_search(query: str, max_results: int) -> list[dict[str, Any]]:
        from duckduckgo_search import DDGS

        with DDGS() as client:
            return list(client.news(query, timelimit="y", max_results=max_results))

    @staticmethod
    def _as_date(value: Any) -> date | None:
        if not value:
            return None
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            return parsed.date()
        except ValueError:
            try:
                return date.fromisoformat(str(value)[:10])
            except ValueError:
                return None
