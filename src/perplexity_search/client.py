"""Programmatic web search via the Perplexity Search API.

Endpoint: POST https://api.perplexity.ai/search (the Python SDK calls it
through `client.search.create`). Returns ranked, structured results — no
LLM-synthesized answer. See https://docs.perplexity.ai/docs/search/quickstart.
"""

from __future__ import annotations

import os
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, Literal

from perplexity import APIStatusError, AuthenticationError, Perplexity, RateLimitError

DEFAULT_MAX_RESULTS = 10
MAX_RESULTS_RANGE = (1, 20)
MAX_QUERIES_PER_REQUEST = 5


class PerplexityConfigError(RuntimeError):
    """Raised when the request can't be configured or the API rejects it (non-429)."""


class PerplexityRateLimitError(RuntimeError):
    """Raised on HTTP 429. Carries the server's Retry-After hint, if any."""

    def __init__(self, message: str, *, retry_after: str | None) -> None:
        super().__init__(message)
        self.retry_after_seconds = float(retry_after) if retry_after else None


@dataclass
class SearchResultItem:
    """One ranked result from the Search API."""

    title: str
    url: str
    snippet: str
    date: str | None
    last_updated: str | None


@dataclass
class SearchAnswer:
    """Result of a search_web() call: ranked results deduped by URL, plus the raw response."""

    id: str
    results: list[SearchResultItem]
    server_time: str | None
    raw: Any = field(repr=False)


def _client() -> Perplexity:
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        raise PerplexityConfigError(
            "PERPLEXITY_API_KEY is not set. Create a key in the API Console "
            "(https://console.perplexity.ai) and export it in your shell, e.g. "
            "`export PERPLEXITY_API_KEY=...` — never pass it as a literal in code."
        )
    return Perplexity(api_key=api_key)


def search_web(
    query: str | Iterable[str],
    *,
    max_results: int = DEFAULT_MAX_RESULTS,
    search_context_size: Literal["low", "medium", "high"] | None = None,
    country: str | None = None,
    search_mode: Literal["web", "academic", "sec"] | None = None,
    search_domain_filter: Iterable[str] | None = None,
    search_language_filter: Iterable[str] | None = None,
    search_recency_filter: Literal["hour", "day", "week", "month", "year"] | None = None,
    search_after_date_filter: str | None = None,
    search_before_date_filter: str | None = None,
    last_updated_after_filter: str | None = None,
    last_updated_before_filter: str | None = None,
) -> SearchAnswer:
    """Run one Search API request.

    `query` is a single string or up to 5 queries; the API fans multiple queries
    out independently and returns one merged, ranked result set in a single
    response, which this wrapper deduplicates by URL (a URL can surface under
    more than one of the queries).
    """
    queries = [query] if isinstance(query, str) else list(query)
    if not 1 <= len(queries) <= MAX_QUERIES_PER_REQUEST:
        raise ValueError(f"query accepts 1 to {MAX_QUERIES_PER_REQUEST} queries per request")
    low, high = MAX_RESULTS_RANGE
    if not low <= max_results <= high:
        raise ValueError(f"max_results must be between {low} and {high}")

    params: dict[str, Any] = {
        "query": query if isinstance(query, str) else queries,
        "max_results": max_results,
    }
    if search_context_size is not None:
        params["search_context_size"] = search_context_size
    if country is not None:
        params["country"] = country
    if search_mode is not None:
        params["search_mode"] = search_mode
    if search_domain_filter is not None:
        params["search_domain_filter"] = list(search_domain_filter)
    if search_language_filter is not None:
        params["search_language_filter"] = list(search_language_filter)
    if search_recency_filter is not None:
        params["search_recency_filter"] = search_recency_filter
    if search_after_date_filter is not None:
        params["search_after_date_filter"] = search_after_date_filter
    if search_before_date_filter is not None:
        params["search_before_date_filter"] = search_before_date_filter
    if last_updated_after_filter is not None:
        params["last_updated_after_filter"] = last_updated_after_filter
    if last_updated_before_filter is not None:
        params["last_updated_before_filter"] = last_updated_before_filter

    client = _client()
    try:
        response = client.search.create(**params)
    except AuthenticationError as exc:
        raise PerplexityConfigError(
            "Perplexity rejected the API key (401 Unauthorized). Verify "
            "PERPLEXITY_API_KEY is correct and active in the API Console "
            "(https://console.perplexity.ai); rotate it there if it may have leaked."
        ) from exc
    except RateLimitError as exc:
        retry_after = exc.response.headers.get("retry-after")
        hint = f" Honor Retry-After: retry in {retry_after}s." if retry_after else ""
        raise PerplexityRateLimitError(
            f"Perplexity rate-limited the request (429).{hint}", retry_after=retry_after
        ) from exc
    except APIStatusError as exc:
        raise PerplexityConfigError(
            f"Perplexity API error {exc.status_code}: {exc.message}"
        ) from exc

    return _to_search_answer(response)


def _to_search_answer(response: Any) -> SearchAnswer:
    seen_urls: set[str] = set()
    results: list[SearchResultItem] = []
    for item in response.results:
        if item.url in seen_urls:
            continue
        seen_urls.add(item.url)
        results.append(
            SearchResultItem(
                title=item.title,
                url=item.url,
                snippet=item.snippet,
                date=item.date,
                last_updated=item.last_updated,
            )
        )
    return SearchAnswer(
        id=response.id,
        results=results,
        server_time=response.server_time,
        raw=response,
    )
