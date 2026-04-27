#!/usr/bin/env python3
"""Mission Control Dashboard for ThePetParentStore — Ploutos Command Center."""
import http.server, json, os, sys, base64, socket

PORT = 18790
WORKSPACE = '/home/node/.openclaw/workspace'

HTML = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Mission Control — Ploutos Command</title>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap" rel="stylesheet">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #000; color: #c8d8f0; font-family: 'Share Tech Mono', monospace; min-height: 100vh; }
  header { padding: 20px 40px; border-bottom: 1px solid #1a4060; display: flex; align-items: center; gap: 20px; }
  header h1 { font-family: 'Orbitron', monospace; color: #4a9eff; font-size: 22px; letter-spacing: 4px; }
  header .sub { color: #3a6090; font-size: 11px; letter-spacing: 2px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; padding: 30px 40px; }
  .card { background: #050d1a; border: 1px solid #1a3050; border-radius: 6px; padding: 20px; }
  .card h2 { font-family: 'Orbitron', monospace; font-size: 11px; color: #3a6090; letter-spacing: 3px; margin-bottom: 15px; }
  .metric { font-size: 36px; font-weight: 900; color: #4a9eff; font-family: 'Orbitron', monospace; }
  .metric-label { font-size: 11px; color: #3a6090; margin-top: 4px; }
  .status-ok { color: #00ff88; }
  .status-warn { color: #ffaa00; }
  .status-err { color: #ff4444; }
  .agent { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid #0a1a2a; }
  .agent:last-child { border-bottom: none; }
  .agent-dot { width: 8px; height: 8px; border-radius: 50%; background: #00ff88; flex-shrink: 0; }
  .agent-name { font-family: 'Orbitron', monospace; font-size: 12px; color: #7ecfff; }
  .agent-role { color: #3a6090; font-size: 10px; }
  footer { padding: 20px 40px; color: #1a3050; font-size: 10px; letter-spacing: 2px; text-align: center; }
</style>
</head>
<body>
<header>
  <div>
    <h1>💰 PLOUTOS MISSION CONTROL</h1>
    <div class="sub">THEPETPARENTSTORE — REAL-TIME OPS</div>
  </div>
</header>
<div class="grid">
  <div class="card">
    <h2>STORE METRICS</h2>
    <div id="listings" class="metric">—</div>
    <div class="metric-label">ACTIVE LISTINGS</div>
  </div>
  <div class="card">
    <h2>SYSTEM STATUS</h2>
    <div class="metric status-ok" id="sys-status">ONLINE</div>
    <div class="metric-label">ALL SYSTEMS</div>
  </div>
  <div class="card">
    <h2>AGENT ROSTER</h2>
    <div class="agent"><div class="agent-dot"></div><div><div class="agent-name">PLOUTOS</div><div class="agent-role">Orchestrator & Financial Partner</div></div></div>
    <div class="agent"><div class="agent-dot"></div><div><div class="agent-name">PADMÉ</div><div class="agent-role">Store Ops — Printify/Etsy</div></div></div>
    <div class="agent"><div class="agent-dot"></div><div><div class="agent-name">ANAKIN</div><div class="agent-role">Developer — KnowLabel</div></div></div>
    <div class="agent"><div class="agent-dot"></div><div><div class="agent-name">CASSIAN</div><div class="agent-role">Intelligence & Briefings</div></div></div>
    <div class="agent"><div class="agent-dot"></div><div><div class="agent-name">R2</div><div class="agent-role">System Monitor</div></div></div>
  </div>
  <div class="card">
    <h2>LATEST INTEL</h2>
    <div id="intel" style="font-size:12px;color:#7ecfff;line-height:1.8;">Loading...</div>
  </div>
</div>
<footer>PLOUTOS COMMAND — <span id="ts"></span></footer>
<script>
document.getElementById('ts').textContent = new Date().toUTCString();
fetch('/api/metrics').then(r=>r.json()).then(d=>{
  document.getElementById('listings').textContent = d.listings || '—';
}).catch(()=>{});
fetch('/api/intel').then(r=>r.json()).then(d=>{
  const lines = (d.content||'No report available.').split('\n').slice(0,8).join('<br>');
  document.getElementById('intel').innerHTML = lines;
}).catch(()=>{document.getElementById('intel').textContent='No data';});
</script>
</body>
</html>
'''

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass

    def do_GET(self):
        try:
            if self.path == '/':
                self._respond(200, 'text/html', HTML.encode())
            elif self.path == '/api/intel':
                try:
                    with open(f'{WORKSPACE}/memory/last-cassian-report.md') as f:
                        full = f.read()
                    lines = [l.strip() for l in full.split('\n') if l.strip() and not l.startswith('#')]
                    content = '\n'.join(lines[:20])
                except:
                    content = 'No report on file yet.'
                    full = content
                self._respond(200, 'application/json', json.dumps({'content': content, 'full': full}).encode())
            elif self.path == '/api/metrics':
                count = '—'
                try:
                    import urllib.request
                    secrets = json.load(open(f'{WORKSPACE}/automation/secrets.json'))
                    key = secrets.get('printify_api_key', '')
                    if key:
                        req = urllib.request.Request(
                            'https://api.printify.com/v1/shops/27174580/products.json?limit=1',
                            headers={'Authorization': f'Bearer {key}'}
                        )
                        with urllib.request.urlopen(req, timeout=5) as r:
                            data = json.loads(r.read())
                            count = data.get('total', '—')
                except:
                    pass
                self._respond(200, 'application/json', json.dumps({'listings': count}).encode())
            else:
                self._respond(404, 'text/plain', b'Not found')
        except Exception:
            pass

    def _respond(self, code, ctype, body):
        self.send_response(code)
        self.send_header('Content-type', ctype)
        self.end_headers()
        self.wfile.write(body)

class RobustHandler(Handler):
    def handle(self):
        try:
            super().handle()
        except Exception:
            pass

if __name__ == '__main__':
    print(f'Mission Control on http://localhost:{PORT}')
    httpd = http.server.HTTPServer(('0.0.0.0', PORT), RobustHandler)
    httpd.serve_forever()
