"""Command-line entry point: `perplexity-search "your query" [query2 ...]`."""

from __future__ import annotations

import argparse
import sys

from .client import PerplexityConfigError, PerplexityRateLimitError, search_web


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run a web search via the Perplexity Search API."
    )
    parser.add_argument(
        "queries", nargs="+", help="One query, or up to 5 searched independently."
    )
    parser.add_argument("--max-results", type=int, default=10, help="1-20 (default: 10).")
    parser.add_argument("--country", default=None, help="ISO 3166-1 alpha-2 country code.")
    parser.add_argument(
        "--search-context-size",
        choices=["low", "medium", "high"],
        default=None,
        help="Snippet depth per result.",
    )
    args = parser.parse_args(argv)

    query: str | list[str] = args.queries[0] if len(args.queries) == 1 else args.queries
    try:
        answer = search_web(
            query,
            max_results=args.max_results,
            country=args.country,
            search_context_size=args.search_context_size,
        )
    except (PerplexityRateLimitError, PerplexityConfigError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    for result in answer.results:
        print(f"{result.title}\n  {result.url}\n  {result.snippet}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
