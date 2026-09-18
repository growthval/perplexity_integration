from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import httpx
import pytest
from perplexity import AuthenticationError, RateLimitError

from perplexity_search.client import (
    PerplexityConfigError,
    PerplexityRateLimitError,
    search_web,
)


def _fake_result(title: str, url: str, snippet: str = "...") -> SimpleNamespace:
    return SimpleNamespace(title=title, url=url, snippet=snippet, date=None, last_updated=None)


def _fake_response(results: list[SimpleNamespace]) -> SimpleNamespace:
    return SimpleNamespace(id="search_123", results=results, server_time=None)


class _FakeSearch:
    def __init__(self, result: Any = None, error: Exception | None = None) -> None:
        self.result = result
        self.error = error
        self.last_kwargs: dict[str, Any] | None = None

    def create(self, **kwargs: Any) -> Any:
        self.last_kwargs = kwargs
        if self.error is not None:
            raise self.error
        return self.result


class _FakeClient:
    def __init__(self, search: _FakeSearch) -> None:
        self.search = search


@pytest.fixture(autouse=True)
def api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PERPLEXITY_API_KEY", "test-key")


def test_search_web_single_query_builds_correct_params(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_search = _FakeSearch(result=_fake_response([_fake_result("A", "https://a.example")]))
    monkeypatch.setattr(
        "perplexity_search.client.Perplexity", lambda api_key: _FakeClient(fake_search)
    )

    answer = search_web("capital of France", max_results=5, country="FR")

    assert fake_search.last_kwargs == {
        "query": "capital of France",
        "max_results": 5,
        "country": "FR",
    }
    assert answer.id == "search_123"
    assert len(answer.results) == 1
    assert answer.results[0].title == "A"
    assert answer.results[0].url == "https://a.example"


def test_search_web_dedupes_results_by_url(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_search = _FakeSearch(
        result=_fake_response(
            [
                _fake_result("A", "https://a.example", "first"),
                _fake_result("A duplicate", "https://a.example", "second"),
                _fake_result("B", "https://b.example"),
            ]
        )
    )
    monkeypatch.setattr(
        "perplexity_search.client.Perplexity", lambda api_key: _FakeClient(fake_search)
    )

    answer = search_web(["query one", "query two"])

    assert [r.url for r in answer.results] == ["https://a.example", "https://b.example"]
    assert answer.results[0].snippet == "first"
    assert fake_search.last_kwargs["query"] == ["query one", "query two"]


def test_search_web_rejects_too_many_queries(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_search = _FakeSearch(result=_fake_response([]))
    monkeypatch.setattr(
        "perplexity_search.client.Perplexity", lambda api_key: _FakeClient(fake_search)
    )

    with pytest.raises(ValueError, match="1 to 5 queries"):
        search_web(["q1", "q2", "q3", "q4", "q5", "q6"])

    assert fake_search.last_kwargs is None


@pytest.mark.parametrize("max_results", [0, 21])
def test_search_web_rejects_out_of_range_max_results(
    monkeypatch: pytest.MonkeyPatch, max_results: int
) -> None:
    fake_search = _FakeSearch(result=_fake_response([]))
    monkeypatch.setattr(
        "perplexity_search.client.Perplexity", lambda api_key: _FakeClient(fake_search)
    )

    with pytest.raises(ValueError, match="max_results"):
        search_web("hello", max_results=max_results)


def test_search_web_missing_api_key_raises_config_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PERPLEXITY_API_KEY", raising=False)

    with pytest.raises(PerplexityConfigError, match="PERPLEXITY_API_KEY is not set"):
        search_web("hello")


def test_search_web_authentication_error_is_wrapped(monkeypatch: pytest.MonkeyPatch) -> None:
    request = httpx.Request("POST", "https://api.perplexity.ai/search")
    http_response = httpx.Response(401, request=request, json={"error": "invalid key"})
    error = AuthenticationError("Unauthorized", response=http_response, body=None)
    fake_search = _FakeSearch(error=error)
    monkeypatch.setattr(
        "perplexity_search.client.Perplexity", lambda api_key: _FakeClient(fake_search)
    )

    with pytest.raises(PerplexityConfigError, match="401"):
        search_web("hello")


def test_search_web_rate_limit_error_carries_retry_after(monkeypatch: pytest.MonkeyPatch) -> None:
    request = httpx.Request("POST", "https://api.perplexity.ai/search")
    http_response = httpx.Response(
        429, request=request, headers={"retry-after": "3"}, json={"error": "rate limited"}
    )
    error = RateLimitError("Too Many Requests", response=http_response, body=None)
    fake_search = _FakeSearch(error=error)
    monkeypatch.setattr(
        "perplexity_search.client.Perplexity", lambda api_key: _FakeClient(fake_search)
    )

    with pytest.raises(PerplexityRateLimitError) as exc_info:
        search_web("hello")

    assert exc_info.value.retry_after_seconds == 3.0
