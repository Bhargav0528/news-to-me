#!/usr/bin/env python3
import json
import os
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
import yfinance as yf

OUT = Path(__file__).resolve().parent
SAMPLES = OUT / 'samples'
SAMPLES.mkdir(parents=True, exist_ok=True)

ALPHA_KEY = os.environ.get('ALPHAVANTAGE_API_KEY', '')
RUNS = 3
SLEEP_SECONDS = 2
AV_REQUEST_DELAY_SECONDS = 15
TIMEOUT = 25

YF_INDICES = {
    'sp500': '^GSPC',
    'nasdaq': '^IXIC',
    'nifty50': '^NSEI',
    'sensex': '^BSESN',
}

AV_SYMBOLS = {
    'sp500': 'SPY',
    'nasdaq': 'QQQ',
    'nifty50': 'NIFTYBEES.BSE',
    'sensex': 'SENSEXBEES.BSE',
}

session = requests.Session()
session.headers.update({'User-Agent': 'news-to-me-poc/1.0'})


def pct(change, prev):
    if prev in (None, 0):
        return None
    return (change / prev) * 100


def yf_fetch(symbol):
    t = yf.Ticker(symbol)
    hist = t.history(period='5d', interval='1d', auto_adjust=False)
    if hist.empty or len(hist) < 2:
        raise RuntimeError(f'No 2-day history for {symbol}')
    latest = hist.iloc[-1]
    prev = hist.iloc[-2]
    close = float(latest['Close'])
    prev_close = float(prev['Close'])
    change = close - prev_close
    return {
        'value': close,
        'change': change,
        'change_percent': pct(change, prev_close),
        'currency': t.fast_info.get('currency') if getattr(t, 'fast_info', None) else None,
        'source_symbol': symbol,
        'as_of': str(hist.index[-1]),
    }


def av_get(params):
    params = dict(params)
    params['apikey'] = ALPHA_KEY
    r = session.get('https://www.alphavantage.co/query', params=params, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def av_fetch(symbol):
    data = av_get({'function': 'GLOBAL_QUOTE', 'symbol': symbol})
    quote = data.get('Global Quote') or {}
    if not quote:
        return {'ok': False, 'symbol': symbol, 'raw': data}
    time.sleep(AV_REQUEST_DELAY_SECONDS)
    return {
        'ok': True,
        'value': float(quote['05. price']) if quote.get('05. price') else None,
        'change': float(quote['09. change']) if quote.get('09. change') else None,
        'change_percent': float(str(quote['10. change percent']).replace('%', '')) if quote.get('10. change percent') else None,
        'source_symbol': symbol,
        'latest_trading_day': quote.get('07. latest trading day'),
        'raw_symbol': quote.get('01. symbol'),
    }


def av_top_movers():
    data = av_get({'function': 'TOP_GAINERS_LOSERS'})
    time.sleep(AV_REQUEST_DELAY_SECONDS)
    return {
        'top_gainers_count': len(data.get('top_gainers') or []),
        'top_losers_count': len(data.get('top_losers') or []),
        'most_actively_traded_count': len(data.get('most_actively_traded') or []),
        'sample_gainer': (data.get('top_gainers') or [None])[0],
        'sample_loser': (data.get('top_losers') or [None])[0],
        'metadata': {k: v for k, v in data.items() if k not in {'top_gainers', 'top_losers', 'most_actively_traded'}},
        'raw': data,
    }


def summarize_stability(values):
    clean = [v for v in values if isinstance(v, (int, float))]
    if not clean:
        return {'ok': False}
    return {
        'ok': True,
        'min': min(clean),
        'max': max(clean),
        'spread': max(clean) - min(clean),
        'mean': statistics.mean(clean),
    }


def main():
    if not ALPHA_KEY:
        raise SystemExit('ALPHAVANTAGE_API_KEY is required')

    results = {
        'ran_at_utc': datetime.now(timezone.utc).isoformat(),
        'runs': [],
        'yfinance': {},
        'alpha_vantage': {},
        'notes': [],
    }

    for run_idx in range(1, RUNS + 1):
        run = {'run': run_idx, 'yfinance': {}, 'alpha_vantage': {}}
        for name, symbol in YF_INDICES.items():
            try:
                run['yfinance'][name] = {'ok': True, **yf_fetch(symbol)}
            except Exception as e:
                run['yfinance'][name] = {'ok': False, 'error': str(e), 'source_symbol': symbol}
        for name, symbol in AV_SYMBOLS.items():
            try:
                run['alpha_vantage'][name] = av_fetch(symbol)
            except Exception as e:
                run['alpha_vantage'][name] = {'ok': False, 'error': str(e), 'source_symbol': symbol}
        try:
            run['alpha_vantage']['top_movers'] = av_top_movers()
        except Exception as e:
            run['alpha_vantage']['top_movers'] = {'ok': False, 'error': str(e)}
        results['runs'].append(run)
        (SAMPLES / f'run-{run_idx}.json').write_text(json.dumps(run, indent=2))
        if run_idx < RUNS:
            time.sleep(SLEEP_SECONDS)

    for source in ('yfinance', 'alpha_vantage'):
        keys = YF_INDICES.keys() if source == 'yfinance' else AV_SYMBOLS.keys()
        for name in keys:
            entries = [r[source][name] for r in results['runs']]
            values = [e.get('value') for e in entries if e.get('ok')]
            changes = [e.get('change_percent') for e in entries if e.get('ok')]
            results[source][name] = {
                'success_runs': sum(1 for e in entries if e.get('ok')),
                'value_stability': summarize_stability(values),
                'change_percent_stability': summarize_stability(changes),
                'latest': next((e for e in reversed(entries) if e.get('ok')), entries[-1]),
            }

    movers_runs = [r['alpha_vantage']['top_movers'] for r in results['runs']]
    results['alpha_vantage']['top_movers'] = {
        'success_runs': sum(1 for e in movers_runs if 'top_gainers_count' in e),
        'latest': movers_runs[-1],
    }

    results['quota_estimate'] = {
        'alpha_vantage_daily_limit': 25,
        'requests_needed_for_daily_indices_plus_movers': 5,
        'feasible_for_single_daily_edition': True,
        'headroom_requests': 20,
    }

    (OUT / 'stock_results.json').write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    main()
