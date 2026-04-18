“””
J.A.R.V.I.S · WEBHOOK SERVER
Recebe alertas do TradingView e repassa ao HUD em tempo real via SSE
“””

from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS
import json, queue, threading, time, os
from datetime import datetime

app = Flask(**name**, static_folder=’.’)
CORS(app)

# ── Fila de eventos SSE (Server-Sent Events) ──

event_queue = queue.Queue()

# ── Webhook secret (configure no TradingView) ──

WEBHOOK_SECRET = os.environ.get(“WEBHOOK_SECRET”, “jarvis2024”)

# ═══════════════════════════════════════════════

# ROTA PRINCIPAL — recebe alertas do TradingView

# ═══════════════════════════════════════════════

@app.route(’/webhook’, methods=[‘POST’])
def webhook():
“””
TradingView envia POST com JSON:
{
“secret”: “jarvis2024”,
“dir”: “LONG”,
“pair”: “XAUUSD”,
“entry”: “3318.50”,
“sl”: “3305.00”,
“tp”: “3345.00”,
“setup”: “AURUM EMA Cross”,
“conf”: 88
}
“””
data = request.get_json(silent=True) or {}

```
# Validação de segurança
if data.get("secret") != WEBHOOK_SECRET:
    return jsonify({"error": "Unauthorized"}), 401

signal = {
    "type": "signal",
    "pair":   data.get("pair",  "XAUUSD"),
    "dir":    data.get("dir",   "LONG").upper(),
    "entry":  data.get("entry", ""),
    "sl":     data.get("sl",    ""),
    "tp":     data.get("tp",    ""),
    "setup":  data.get("setup", "TradingView Alert"),
    "source": "TradingView",
    "conf":   data.get("conf",  85),
    "ts":     datetime.now().strftime("%H:%M:%S")
}

event_queue.put(signal)
print(f"[SIGNAL] {signal['dir']} {signal['pair']} @ {signal['entry']}")
return jsonify({"status": "ok", "signal": signal}), 200
```

# ═══════════════════════════════════════════════

# ROTA MT5 — recebe sinais do EA Python Bridge

# ═══════════════════════════════════════════════

@app.route(’/mt5’, methods=[‘POST’])
def mt5_signal():
data = request.get_json(silent=True) or {}
signal = {
“type”:   “signal”,
“pair”:   data.get(“pair”,  “XAUUSD”),
“dir”:    data.get(“dir”,   “LONG”).upper(),
“entry”:  str(data.get(“entry”, “”)),
“sl”:     str(data.get(“sl”,    “”)),
“tp”:     str(data.get(“tp”,    “”)),
“setup”:  data.get(“setup”, “AURUM VENATRIX EA”),
“source”: “MT5 EA”,
“conf”:   data.get(“conf”,  90),
“ts”:     datetime.now().strftime(”%H:%M:%S”)
}
event_queue.put(signal)
print(f”[MT5] {signal[‘dir’]} {signal[‘pair’]}”)
return jsonify({“status”: “ok”}), 200

# ═══════════════════════════════════════════════

# SSE — envia eventos ao HUD em tempo real

# ═══════════════════════════════════════════════

@app.route(’/events’)
def sse():
“”“HUD se conecta aqui via EventSource para receber sinais em tempo real”””
def stream():
# Heartbeat inicial
yield f”data: {json.dumps({‘type’:‘connected’,‘msg’:‘JARVIS SSE Online’})}\n\n”
while True:
try:
event = event_queue.get(timeout=25)
yield f”data: {json.dumps(event)}\n\n”
except queue.Empty:
# Heartbeat a cada 25s para manter conexão viva
yield f”data: {json.dumps({‘type’:‘ping’,‘ts’:datetime.now().strftime(’%H:%M:%S’)})}\n\n”

```
return Response(
    stream(),
    mimetype='text/event-stream',
    headers={
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no',
        'Access-Control-Allow-Origin': '*'
    }
)
```

# ═══════════════════════════════════════════════

# ROTA STATUS

# ═══════════════════════════════════════════════

@app.route(’/status’)
def status():
return jsonify({
“status”: “online”,
“service”: “JARVIS Webhook Server”,
“version”: “1.0.0”,
“ts”: datetime.now().isoformat()
})

# ═══════════════════════════════════════════════

# ROTA TESTE — simula sinal manual

# ═══════════════════════════════════════════════

@app.route(’/test-signal’)
def test_signal():
signal = {
“type”: “signal”,
“pair”: “XAUUSD”, “dir”: “LONG”,
“entry”: “3318.50”, “sl”: “3305.00”, “tp”: “3345.00”,
“setup”: “TEST — AURUM EMA Cross”,
“source”: “Test”, “conf”: 99,
“ts”: datetime.now().strftime(”%H:%M:%S”)
}
event_queue.put(signal)
return jsonify({“status”: “test signal sent”})

if **name** == ‘**main**’:
port = int(os.environ.get(“PORT”, 5000))
print(f”\n🤖 J.A.R.V.I.S Webhook Server rodando na porta {port}”)
print(f”   POST /webhook  → TradingView alerts”)
print(f”   POST /mt5      → MT5 EA signals”)
print(f”   GET  /events   → SSE stream para o HUD”)
print(f”   GET  /status   → health check\n”)
app.run(host=‘0.0.0.0’, port=port, debug=False, threaded=True)
