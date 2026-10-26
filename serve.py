#!/usr/bin/env python3
"""Tiny static server WITH HTTP Range support (python -m http.server has none, so browsers cannot seek or stream video
properly: scroll-scrubbed video and loops stutter or fail). Usage: python3 serve.py [port] [folder]"""
import os, re, sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
class H(SimpleHTTPRequestHandler):
    def send_head(self):
        rng = self.headers.get('Range'); path = self.translate_path(self.path)
        if not rng or not os.path.isfile(path): return super().send_head()
        m = re.match(r'bytes=(\d*)-(\d*)', rng)
        if not m: return super().send_head()
        size = os.path.getsize(path); a = int(m.group(1)) if m.group(1) else None; b = int(m.group(2)) if m.group(2) else None
        if a is None: a, b = max(0, size - b), size - 1
        else: b = size - 1 if b is None else min(b, size - 1)
        if a > b or a >= size: self.send_error(416); return None
        f = open(path, 'rb'); f.seek(a); self.send_response(206)
        self.send_header('Content-Type', self.guess_type(path)); self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Range', f'bytes {a}-{b}/{size}'); self.send_header('Content-Length', str(b - a + 1)); self.end_headers()
        self.range = (a, b); return f
    def copyfile(self, src, dst):
        r = getattr(self, 'range', None)
        if r: self.range = None; left = r[1] - r[0] + 1
        else: left = None
        while True:
            chunk = src.read(65536 if left is None else min(65536, left))
            if not chunk: break
            try: dst.write(chunk)
            except (BrokenPipeError, ConnectionResetError): break
            if left is not None:
                left -= len(chunk)
                if left <= 0: break
    def end_headers(self):
        self.send_header('Accept-Ranges', 'bytes'); super().end_headers()
    def log_message(self, *a): pass
if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    if len(sys.argv) > 2: os.chdir(sys.argv[2])
    print('serving on http://localhost:%d (Range enabled)' % port); ThreadingHTTPServer(('', port), H).serve_forever()
