#!/usr/bin/env python3
"""Minimal real-request smoke test for the Perplexity Search API integration.

Requires PERPLEXITY_API_KEY to be exported in the environment already —
this script never prompts for or prints the key. Run with:

    python scripts/search_smoke_test.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from perplexity_search.client import (  # noqa: E402
    PerplexityConfigError,
    PerplexityRateLimitError,
    search_web,
)


def main() -> int:
    if not os.environ.get("PERPLEXITY_API_KEY"):
        print(
            "PERPLEXITY_API_KEY is not set. Create a key at https://console.perplexity.ai "
            "and export it in your shell, then re-run this script.",
            file=sys.stderr,
        )
        return 1

    try:
        answer = search_web("capital of France", max_results=3)
    except PerplexityRateLimitError as exc:
        print(f"HTTP 429 (rate limited): {exc}")
        return 1
    except PerplexityConfigError as exc:
        print(f"request failed: {exc}")
        return 1

    print("HTTP 200 OK")
    print(f"search_id={answer.id} result_count={len(answer.results)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
