#!/usr/bin/env python3
# MeshCore Emergency AI Failover - Joe/Clem Heavyside
# N100 + OpenWebUI + Starlink + Ollama + GUZMAN channel
# No API keys in code - use environment variables only
import subprocess, requests, time, os, json
from datetime import datetime

# CONFIG - set these for your N100 machine
OPENWEBUI_URL = os.getenv("OPENWEBUI_URL", "http://localhost:3000")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
PRIMARY_IF = os.getenv("PRIMARY_IF", "eth0")
STARLINK_IF = os.getenv("STARLINK_IF", "eth1")
PING_HOST = "8.8.8.8"
CHECK_INTERVAL = 30

def ping(interface=None):
  cmd = ["ping","-c","1","-W","2", PING_HOST]
  if interface: cmd += ["-I", interface]
    try: return subprocess.call(cmd, stdout=subprocess.DEVNULL) == 0
      except: return False

def ollama_ok():
  try: return requests.get(f"{OLLAMA_URL}/api/tags",timeout=2).status_code==200
    except: return False

def get_connection():
  if ping(PRIMARY_IF): return "ISP"
    if ping(STARLINK_IF): return "STARLINK"
      if ollama_ok(): return "OLLAMA"
        return "MESHCORE_ONLY"

def ask_ai(prompt, conn):
  if conn in ["ISP","STARLINK"]:
    try:
      r = requests.post(f"{OPENWEBUI_URL}/api/chat/completions",
                        json={"model":"claude-3-5-sonnet-20241022",
                              "messages":[{"role":"user","content":prompt}]},
                        timeout=15)
      return r.json()["choices"][0]["message"]["content"]
      except: pass
        try:
          r = requests.post(f"{OLLAMA_URL}/api/generate",
                            json={"model":"llama3","prompt":prompt,"stream":False},timeout=30)
          return r.json()["response"]
          except: return "[AI UNAVAILABLE] MeshCore hardware comms only"

def guzman(msg):
  """Send to GUZMAN channel - max 133 chars per message"""
chunks = [msg[i:i+133] for i in range(0, len(msg), 133)]
for i, chunk in enumerate(chunks):
  prefix = f"[P{i+1}/{len(chunks)}] " if len(chunks)>1 else ""
print(f"[GUZMAN] {datetime.now().strftime('%H:%M')} >> {prefix}{chunk}")
# TODO: wire up MeshCore BLE companion protocol

def status_alert(conn):
  alerts = {
    "ISP":          "🟢 ISP ONLINE. Claude AI via OpenWebUI active.",
    "STARLINK":     "🛰️ ISP DOWN. Starlink fallback active. AI operational.",
    "OLLAMA":       "⚠️ Internet DOWN. Local Ollama on N100 active.",
    "MESHCORE_ONLY":"🔴 ALL DOWN. MeshCore ONLY. Solar power OK. No AI."
  }
return alerts.get(conn, "❓ Unknown connection state")

def main():
  print("[BOOT] MeshCore Emergency AI Failover - Joe/Clem Heavyside")
last_conn = None
while True:
  conn = get_connection()
if conn != last_conn:
  alert = status_alert(conn)
print(f"[NET] Connection changed: {last_conn} -> {conn}")
guzman(alert)
last_conn = conn
time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
  main()
