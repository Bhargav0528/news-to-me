"""Fetcher package exports for News To Me."""

from .article_fetcher import ArticleFetcher, ExtractionResult, results_to_json

__all__ = ["ArticleFetcher", "ExtractionResult", "results_to_json"]
