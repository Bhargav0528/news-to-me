"""Market snapshot fetcher for the News To Me pipeline."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

import yfinance as yf


@dataclass
class MarketIndexSnapshot:
    """Structured snapshot for a tracked stock index."""

    name: str
    symbol: str
    value: float
    change: float
    change_percent: float

    def to_dict(self) -> dict[str, Any]:
        """Return the snapshot as a serializable dictionary."""
        return asdict(self)


class StockFetcher:
    """Fetch daily market data for the four tracked indices."""

    INDEX_MAP = {
        "S&P 500": "^GSPC",
        "NASDAQ": "^IXIC",
        "NIFTY 50": "^NSEI",
        "SENSEX": "^BSESN",
    }

    def fetch_snapshot(self) -> dict[str, list[dict[str, Any]]]:
        """Fetch structured market snapshots for all tracked indices."""
        indices: list[dict[str, Any]] = []
        for name, symbol in self.INDEX_MAP.items():
            ticker = yf.Ticker(symbol)
            history = ticker.history(period="5d", interval="1d", auto_adjust=False)
            if history.empty or len(history) < 2:
                raise RuntimeError(f"Insufficient history for {symbol}")
            latest = history.iloc[-1]
            previous = history.iloc[-2]
            value = float(latest["Close"])
            previous_close = float(previous["Close"])
            change = value - previous_close
            change_percent = (change / previous_close) * 100 if previous_close else 0.0
            indices.append(
                MarketIndexSnapshot(
                    name=name,
                    symbol=symbol,
                    value=value,
                    change=change,
                    change_percent=change_percent,
                ).to_dict()
            )
        return {"indices": indices}
