"""Massive REST client for the fetch concern (see PRIOR-ART.md sections 6 and 7).

- Key is read at call time from a file (MASSIVE_KEY_FILE, else the default archived path)
  and sent only as a Bearer header. It is never logged, printed, stored or put in a URL.
- Retries 429/5xx/network errors with exponential backoff plus jitter; honours Retry-After.
- Shared token-bucket pacing (MASSIVE_MAX_RPS, default 15 requests/second across threads).
- Circuit breaker: after BREAKER_THRESHOLD consecutive hard failures (401/403/other 4xx,
  or exhausted retries) every caller gets CircuitOpen, so an expired account stops the
  run in seconds instead of producing hundreds of identical failures.
- Follows `next_url` for pagination; any apiKey in a returned URL is stripped.
- No writes to any data folder.
"""
import json, os, random, threading, time, urllib.request, urllib.parse, urllib.error

BASE = "https://api.massive.com"
MAX_RPS = float(os.environ.get("MASSIVE_MAX_RPS", "15"))
BREAKER_THRESHOLD = int(os.environ.get("MASSIVE_BREAKER", "8"))


class CircuitOpen(RuntimeError):
    pass


_lock = threading.Lock()
_next_slot = 0.0
_consecutive_hard_failures = 0
_breaker_open = False


def _pace():
    """Token-bucket style pacing: hand out request start times 1/MAX_RPS apart."""
    global _next_slot
    with _lock:
        now = time.monotonic()
        slot = max(now, _next_slot)
        _next_slot = slot + 1.0 / MAX_RPS
    if slot > now:
        time.sleep(slot - now)


def _record(ok):
    global _consecutive_hard_failures, _breaker_open
    with _lock:
        if ok:
            _consecutive_hard_failures = 0
        else:
            _consecutive_hard_failures += 1
            if _consecutive_hard_failures >= BREAKER_THRESHOLD:
                _breaker_open = True


def _key():
    p = os.environ.get("MASSIVE_KEY_FILE")
    if not p:
        raise RuntimeError("Set MASSIVE_KEY_FILE to an existing credential file")
    with open(p, "r", encoding="utf-8") as fh:
        k = fh.read().strip()
    if not k:
        raise RuntimeError("key file is empty: %s" % p)
    return k


def _sleep_backoff(attempt, retry_after=None):
    base = min(60.0, 1.5 * (2 ** attempt))
    wait = float(retry_after) if retry_after else base
    time.sleep(wait * (0.5 + random.random()))  # jitter: 50%-150%


def get(path_or_url, params=None, max_retries=6, timeout=60):
    """GET one URL; returns (status, parsed_json_or_None, response_headers_subset)."""
    if _breaker_open:
        raise CircuitOpen("circuit breaker open after %d consecutive hard failures" % BREAKER_THRESHOLD)
    url = path_or_url if path_or_url.startswith("http") else BASE + path_or_url
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    u = urllib.parse.urlsplit(url)
    q = [(k, v) for k, v in urllib.parse.parse_qsl(u.query, keep_blank_values=True) if k.lower() != "apikey"]
    url = urllib.parse.urlunsplit((u.scheme, u.netloc, u.path, urllib.parse.urlencode(q), ""))
    last = None
    for a in range(max_retries):
        _pace()
        req = urllib.request.Request(url, headers={"Authorization": "Bearer " + _key(), "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = json.loads(r.read().decode("utf-8"))
                hdr = {k: v for k, v in r.headers.items() if k.lower().startswith(("x-ratelimit", "retry-after"))}
                _record(True)
                return r.status, body, hdr
        except urllib.error.HTTPError as e:
            last = "HTTP %d" % e.code
            if e.code in (429, 500, 502, 503, 504):
                _sleep_backoff(a, e.headers.get("Retry-After"))
                continue
            try:
                detail = json.loads(e.read().decode("utf-8"))
            except Exception:
                detail = None
            _record(False)  # 4xx other than 429: not going to fix itself on retry
            return e.code, detail, {}
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            last = type(e).__name__
            _sleep_backoff(a)
    _record(False)
    raise RuntimeError("exhausted retries (%s) for %s" % (last, u.path))


def aggs(ticker, mult, span, start, end, adjusted="true", limit=50000):
    """Yield (status, page_json, headers) for every page of /v2/aggs for one ticker/range."""
    path = "/v2/aggs/ticker/%s/range/%d/%s/%s/%s" % (urllib.parse.quote(ticker, safe=""), mult, span, start, end)
    status, body, hdr = get(path, {"adjusted": adjusted, "sort": "asc", "limit": limit})
    while True:
        yield status, body, hdr
        nxt = body.get("next_url") if isinstance(body, dict) else None
        if status != 200 or not nxt:
            return
        status, body, hdr = get(nxt)
