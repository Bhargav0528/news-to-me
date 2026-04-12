from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable, List, Optional

import requests
import trafilatura
from bs4 import BeautifulSoup
from readability import Document

DEFAULT_USER_AGENT = "NewsToMeBot/1.0 (+https://mrmain.atlassian.net)"
DEFAULT_TIMEOUT_SECONDS = 20
DEFAULT_DELAY_SECONDS = 1.2
MIN_TEXT_CHARS = 400


@dataclass
class ExtractionResult:
    url: str
    final_url: Optional[str]
    success: bool
    method: Optional[str]
    title: Optional[str]
    text: str
    text_length: int
    status_code: Optional[int]
    error: Optional[str] = None
    blocked: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ArticleFetcher:
    def __init__(
        self,
        *,
        user_agent: str = DEFAULT_USER_AGENT,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        delay_seconds: float = DEFAULT_DELAY_SECONDS,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.user_agent = user_agent
        self.timeout_seconds = timeout_seconds
        self.delay_seconds = delay_seconds
        self.session = session or requests.Session()
        self.session.headers.update(
            {
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.8",
            }
        )

    def fetch_article(self, url: str) -> ExtractionResult:
        try:
            response = self.session.get(url, timeout=self.timeout_seconds)
        except requests.RequestException as exc:
            return ExtractionResult(
                url=url,
                final_url=None,
                success=False,
                method=None,
                title=None,
                text="",
                text_length=0,
                status_code=None,
                error=str(exc),
            )

        blocked = response.status_code in {401, 402, 403, 406, 410, 451, 429}
        html = response.text or ""
        title = self._extract_title(html)

        extractors = [
            ("trafilatura", self._extract_with_trafilatura),
            ("readability", self._extract_with_readability),
            ("meta_fallback", self._extract_with_meta),
        ]

        last_error = None
        for method_name, extractor in extractors:
            try:
                text = self._normalize_text(extractor(html, response.url))
            except Exception as exc:  # pragma: no cover - defensive fallback path
                last_error = f"{method_name}: {exc}"
                continue
            if len(text) >= MIN_TEXT_CHARS:
                return ExtractionResult(
                    url=url,
                    final_url=response.url,
                    success=True,
                    method=method_name,
                    title=title,
                    text=text,
                    text_length=len(text),
                    status_code=response.status_code,
                    blocked=blocked,
                )

        return ExtractionResult(
            url=url,
            final_url=response.url,
            success=False,
            method=None,
            title=title,
            text="",
            text_length=0,
            status_code=response.status_code,
            error=last_error or f"No extractor produced >= {MIN_TEXT_CHARS} chars",
            blocked=blocked,
        )

    def fetch_articles(self, urls: Iterable[str]) -> List[ExtractionResult]:
        results: List[ExtractionResult] = []
        for index, url in enumerate(urls):
            if index:
                time.sleep(self.delay_seconds)
            results.append(self.fetch_article(url))
        return results

    def enrich_records(self, records: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        enriched: List[Dict[str, Any]] = []
        for index, record in enumerate(records):
            if index:
                time.sleep(self.delay_seconds)
            result = self.fetch_article(record["url"])
            payload = dict(record)
            payload["full_text"] = result.text or None
            payload["full_text_length"] = result.text_length
            payload["fetch_status"] = "ok" if result.success else "failed"
            payload["fetch_method"] = result.method
            payload["fetch_error"] = result.error
            payload["resolved_url"] = result.final_url
            payload["http_status"] = result.status_code
            enriched.append(payload)
        return enriched

    def enrich_sqlite(self, db_path: str, table_name: str = "articles") -> int:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                f"SELECT rowid, url FROM {table_name} WHERE url IS NOT NULL AND (full_text IS NULL OR full_text = '')"
            ).fetchall()
            updated = 0
            for index, row in enumerate(rows):
                if index:
                    time.sleep(self.delay_seconds)
                result = self.fetch_article(row["url"])
                conn.execute(
                    f"UPDATE {table_name} SET full_text = ?, full_text_length = ?, fetch_status = ?, fetch_method = ?, fetch_error = ? WHERE rowid = ?",
                    (
                        result.text if result.success else None,
                        result.text_length,
                        "ok" if result.success else "failed",
                        result.method,
                        result.error,
                        row["rowid"],
                    ),
                )
                updated += 1
            conn.commit()
            return updated
        finally:
            conn.close()

    @staticmethod
    def _extract_with_trafilatura(html: str, url: str) -> str:
        return trafilatura.extract(
            html,
            url=url,
            include_comments=False,
            include_links=False,
            favor_precision=True,
            output_format="txt",
        ) or ""

    @staticmethod
    def _extract_with_readability(html: str, url: str) -> str:
        document = Document(html)
        content_html = document.summary(html_partial=True)
        soup = BeautifulSoup(content_html, "html.parser")
        return soup.get_text("\n", strip=True)

    @staticmethod
    def _extract_with_meta(html: str, url: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        selectors = [
            'meta[property="og:description"]',
            'meta[name="description"]',
            'article',
            'main',
        ]
        chunks: List[str] = []
        for selector in selectors:
            node = soup.select_one(selector)
            if not node:
                continue
            if node.name == "meta":
                value = node.get("content", "").strip()
            else:
                value = node.get_text("\n", strip=True)
            if value:
                chunks.append(value)
        return "\n\n".join(chunks)

    @staticmethod
    def _extract_title(html: str) -> Optional[str]:
        soup = BeautifulSoup(html, "html.parser")
        if soup.title and soup.title.text:
            return soup.title.text.strip()
        meta = soup.select_one('meta[property="og:title"]')
        if meta and meta.get("content"):
            return meta["content"].strip()
        return None

    @staticmethod
    def _normalize_text(text: str) -> str:
        lines = [line.strip() for line in text.splitlines()]
        return "\n".join(line for line in lines if line)


def results_to_json(results: Iterable[ExtractionResult]) -> str:
    return json.dumps([result.to_dict() for result in results], indent=2, ensure_ascii=False)
