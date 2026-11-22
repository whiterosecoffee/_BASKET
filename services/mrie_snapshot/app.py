"""Local REST component; not a production server or MCP transport."""
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import time
from http.server import BaseHTTPRequestHandler, HTTPServer


def build_snapshot(root, source_sha):
    if not re.fullmatch(r'[0-9a-f]{40}', source_sha):
        raise ValueError('exact source commit required')
    root = Path(root).resolve()
    records = {}
    for entity in sorted((root / 'tickers').glob('*/entity.json')):
        ticker = entity.parent.name
        if not re.fullmatch(r'[A-Z0-9][A-Z0-9.-]{0,15}', ticker):
            raise ValueError('invalid ticker directory')
        if entity.is_symlink() or entity.parent.is_symlink():
            raise ValueError('symlink input rejected')
        raw = entity.read_bytes()
        if len(raw) > 65536:
            raise ValueError('entity too large')
        value = json.loads(raw)
        if not isinstance(value, dict) or value.get('id') != ticker:
            raise ValueError('entity identity mismatch')
        records[ticker] = dict(entity=value, source_path=entity.relative_to(root).as_posix(),
                               input_sha256=hashlib.sha256(raw).hexdigest(),
                               status='historical_unverified', as_of=None, live=False)
    if not records:
        raise ValueError('empty snapshot')
    manifest = json.dumps(dict(source_sha=source_sha, records=records), sort_keys=True,
                          separators=(',', ':')).encode()
    # Serialize once; filesystem changes cannot mutate this process snapshot.
    return manifest, hashlib.sha256(manifest).hexdigest()


def make_server(root, source_sha, token, address=('127.0.0.1', 0), limit=60):
    if len(token) < 32 or not token.isascii():
        raise ValueError('strong ASCII bearer token required')
    frozen, digest = build_snapshot(root, source_sha)
    snapshot = json.loads(frozen)
    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(5)
        def log_message(self, *args):
            pass  # Never log headers, tokens, URLs, or response payloads.
        def reply(self, code, value):
            data = json.dumps(dict(value, source_sha=source_sha, snapshot_sha256=digest)).encode()
            self.send_response(code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(data)
        def do_GET(self):
            if self.path == '/health':
                return self.reply(200, dict(status='ok', mode='read_only_snapshot', live=False))
            supplied = self.headers.get('Authorization', '')
            if not hmac.compare_digest(supplied.encode(), ('Bearer ' + token).encode()):
                return self.reply(401, dict(error='unauthorized'))
            now = time.monotonic()
            self.server.calls[:] = [t for t in self.server.calls if now-t < 60]
            if len(self.server.calls) >= limit:
                return self.reply(429, dict(error='rate_limited'))
            self.server.calls.append(now)
            if self.path == '/tools':
                return self.reply(200, dict(protocol='REST-only', tools=['ticker_snapshot']))
            match = re.fullmatch(r'/snapshot/([A-Z0-9][A-Z0-9.-]{0,15})', self.path)
            if not match:
                return self.reply(400, dict(error='invalid_request'))
            record = snapshot['records'].get(match[1])
            return self.reply(200, dict(ticker=match[1], result=record or dict(
                status='unavailable', live=False, as_of=None)))
    server = HTTPServer(address, Handler)
    server.calls = []
    return server


if __name__ == '__main__':
    # Loopback-only: use a reviewed production gateway before external exposure.
    make_server(os.environ['MRIE_ROOT'], os.environ['MRIE_SOURCE_SHA'],
                os.environ['MRIE_TOKEN'], ('127.0.0.1', int(os.environ.get('PORT', '8080')))).serve_forever()
