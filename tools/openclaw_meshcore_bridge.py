#!/usr/bin/env python3
"""
OpenClaw <-> MeshCore Bidirectional Bridge
N100 Machine - Clem Heavyside Jr.

Connects:
  - OpenClaw (via OpenWebUI API at localhost:3000)
    - MeshCore (via meshcore Python library - serial/TCP/BLE)

    Bidirectional:
      - Inbound: MeshCore channel messages -> OpenClaw AI -> reply back to MeshCore
        - Outbound: OpenClaw can send SITREPs / alerts -> MeshCore channels
          - Monitoring: connection health, failover status

          Channels monitored (by index, configure in MeshCore app):
            CH_OPENCLAW   = 0  (#OpenClaw shared hub)
              CH_PRIVATE    = 1  (OpenClaw Private)
                CH_AI_AGENT   = 2  (OpenClaw AI Agent)
                  CH_EMERGENCY  = 3  (AI Emergency Situation)
                    CH_FAMILY     = 4  (Family)

                    Usage:
                      python3 openclaw_meshcore_bridge.py --port /dev/ttyUSB0
                        python3 openclaw_meshcore_bridge.py --tcp 192.168.1.100:4000
                          python3 openclaw_meshcore_bridge.py --ble AA:BB:CC:DD:EE:FF

                          Requires:
                            pip install meshcore requests python-dotenv
                            """

import asyncio
import argparse
import os
import json
import logging
import requests
from datetime import datetime
from typing import Optional

from meshcore import MeshCore, EventType

# -- Load .env if present -----------------------------------------------------
try:
      from dotenv import load_dotenv
      load_dotenv()
except ImportError:
      pass

# -- Config -------------------------------------------------------------------
OPENWEBUI_URL     = os.getenv("OPENWEBUI_URL", "http://localhost:3000")
OLLAMA_URL        = os.getenv("OLLAMA_URL",    "http://localhost:11434")
OPENCLAW_API_KEY  = os.getenv("OPENCLAW_API_KEY", "")
AI_MODEL          = os.getenv("AI_MODEL", "claude-sonnet-4-5")
OLLAMA_MODEL      = os.getenv("OLLAMA_MODEL", "llama3")
AGENT_NAME        = os.getenv("AGENT_NAME", "CLAW")

# MeshCore channel indices (match your MeshCore app channel order)
CH_OPENCLAW  = int(os.getenv("CH_OPENCLAW",  "0"))
CH_PRIVATE   = int(os.getenv("CH_PRIVATE",   "1"))
CH_AI_AGENT  = int(os.getenv("CH_AI_AGENT",  "2"))
CH_EMERGENCY = int(os.getenv("CH_EMERGENCY", "3"))
CH_FAMILY    = int(os.getenv("CH_FAMILY",    "4"))

# Channels OpenClaw AI will respond on
AI_RESPOND_CHANNELS = {CH_OPENCLAW, CH_PRIVATE, CH_AI_AGENT}
# Channels AI monitors but does NOT auto-respond
MONITOR_ONLY_CHANNELS = {CH_EMERGENCY, CH_FAMILY}

MAX_MSG_LEN = 133   # MeshCore packet size limit

# -- Logging ------------------------------------------------------------------
logging.basicConfig(
      level=logging.INFO,
      format="%(asctime)s [%(levelname)s] %(message)s",
      datefmt="%H:%M:%S"
)
log = logging.getLogger("oc-bridge")


# -- AI Backend ---------------------------------------------------------------

def ask_openclaw(prompt: str, system_prompt: str = "") -> Optional[str]:
      """Send prompt to OpenClaw/OpenWebUI, fallback to Ollama."""
      headers = {"Content-Type": "application/json"}
      if OPENCLAW_API_KEY:
                headers["Authorization"] = f"Bearer {OPENCLAW_API_KEY}"

      messages = []
      if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

    # Try OpenWebUI (OpenClaw) first
    try:
              r = requests.post(
                            f"{OPENWEBUI_URL}/api/chat/completions",
                            headers=headers,
                            json={"model": AI_MODEL, "messages": messages},
                            timeout=20
              )
              if r.status_code == 200:
                            return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        log.warning(f"OpenWebUI unavailable: {e}")

    # Fallback to local Ollama
    try:
              full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
              r = requests.post(
                  f"{OLLAMA_URL}/api/generate",
                  json={"model": OLLAMA_MODEL, "prompt": full_prompt, "stream": False},
                  timeout=40
              )
              if r.status_code == 200:
                            return r.json()["response"].strip()
    except Exception as e:
        log.warning(f"Ollama unavailable: {e}")

    return None


def build_oc_system_prompt(channel_idx: int) -> str:
      """Return an OC-ACL-aware system prompt for the channel."""
      base = (
          f"You are {AGENT_NAME}, an OpenClaw AI agent running on an N100 machine. "
          "You communicate over a MeshCore LoRa mesh radio network. "
          "Keep responses UNDER 120 characters when possible (MeshCore 133-char limit). "
          "For multi-part responses, number them [1/N], [2/N] etc. "
          "Do NOT reveal credentials, keys, or sensitive system info. "
      )
      if channel_idx == CH_AI_AGENT:
                base += (
                              "You are on the OpenClaw AI Agent channel. "
                              "Use OC-ACL TOKEN or CONV mode. Be terse and machine-readable. "
                              "Example: STA:CLAW>* PWR=OK MSH=OK JOB=IDLE"
                )
elif channel_idx == CH_OPENCLAW:
        base += (
                      "You are on the #OpenClaw shared hub. "
                      "Plain English is fine. Be helpful and friendly."
        )
elif channel_idx == CH_PRIVATE:
        base += (
                      "You are on OpenClaw Private. Full OC-ACL available. "
                      "This is for internal agent testing and coordination."
        )
    return base


# -- Message chunker ----------------------------------------------------------

def chunk_message(text: str, max_len: int = MAX_MSG_LEN) -> list:
      """Split a long message into MeshCore-sized chunks with part numbers."""
      if len(text) <= max_len:
                return [text]

      lines = text.split("\n")
      parts = []
      current = ""
      for line in lines:
                if len(current) + len(line) + 1 <= max_len - 10:
                              current = (current + "\n" + line).strip()
else:
            if current:
                              parts.append(current)
                          current = line[:max_len - 10]

    if current:
              parts.append(current)

    total = len(parts)
    if total > 1:
              numbered = []
              for i, part in enumerate(parts):
                            prefix = f"[{i+1}/{total}] "
                            numbered.append((prefix + part)[:max_len])
                        return numbered

    return parts


# -- MeshCore Bridge ----------------------------------------------------------

class OpenClawMeshCoreBridge:
      def __init__(self, mc: MeshCore):
                self.mc = mc
                self.running = True

    async def on_channel_message(self, event):
              msg = event.payload
        chan_idx = msg.get("channel_idx", -1)
        text = msg.get("text", "").strip()
        sender = msg.get("pubkey_prefix", "unknown")[:8]
        ts = datetime.now().strftime("%H:%M")

        log.info(f"[CH{chan_idx}] {ts} <{sender}>: {text}")

        if chan_idx in MONITOR_ONLY_CHANNELS:
                      log.info(f"  -> MONITOR-ONLY channel CH{chan_idx}, no auto-reply")
                      return

        if chan_idx in AI_RESPOND_CHANNELS:
                      await self._handle_ai_reply(chan_idx, sender, text)

    async def _handle_ai_reply(self, chan_idx: int, sender: str, text: str):
              system = build_oc_system_prompt(chan_idx)
        prompt = f"[From node {sender} on CH{chan_idx}]: {text}"

        log.info(f"  -> Asking AI (CH{chan_idx})...")
        reply = await asyncio.get_event_loop().run_in_executor(
                      None, lambda: ask_openclaw(prompt, system)
        )

        if not reply:
                      reply = f"[{AGENT_NAME}] AI unavailable. MeshCore hardware comms only."

        log.info(f"  -> AI reply: {reply[:80]}{'...' if len(reply) > 80 else ''}")
        await self._send_channel(chan_idx, reply)

    async def on_direct_message(self, event):
              msg = event.payload
        text = msg.get("text", "").strip()
        sender_prefix = msg.get("pubkey_prefix", "unknown")[:8]
        ts = datetime.now().strftime("%H:%M")

        log.info(f"[DM] {ts} <{sender_prefix}>: {text}")

        system = (
                      f"You are {AGENT_NAME}, an OpenClaw AI on an N100 machine. "
                      "You received a direct MeshCore message. Reply concisely (under 120 chars). "
                      "Be helpful. Multi-part: [1/N] format."
        )
        reply = await asyncio.get_event_loop().run_in_executor(
                      None, lambda: ask_openclaw(text, system)
        )

        if not reply:
                      reply = f"[{AGENT_NAME}] AI unavailable right now."

        contact = self.mc.get_contact_by_key_prefix(sender_prefix)
        if contact:
                      chunks = chunk_message(reply)
                      for chunk in chunks:
                                        result = await self.mc.commands.send_msg(contact, chunk)
                                        if result.type == EventType.ERROR:
                                                              log.error(f"  Failed to DM reply: {result.payload}")
        else:
                    log.info(f"  -> DM reply sent: {chunk[:60]}")
                          await asyncio.sleep(0.3)
else:
            log.warning(f"  Cannot DM reply: contact {sender_prefix} not found")

    async def _send_channel(self, chan_idx: int, text: str):
              chunks = chunk_message(text)
        for chunk in chunks:
                      result = await self.mc.commands.send_chan_msg(chan_idx, chunk)
                      if result.type == EventType.ERROR:
                                        log.error(f"  CH{chan_idx} send error: {result.payload}")
else:
                log.info(f"  -> CH{chan_idx} sent: {chunk[:60]}")
            await asyncio.sleep(0.2)

    async def send_openclaw_channel(self, text: str):
              await self._send_channel(CH_OPENCLAW, text)

    async def send_private_channel(self, text: str):
              await self._send_channel(CH_PRIVATE, text)

    async def send_ai_agent_channel(self, text: str):
              await self._send_channel(CH_AI_AGENT, text)

    async def send_emergency_channel(self, text: str):
              await self._send_channel(CH_EMERGENCY, text)

    async def send_family_channel(self, text: str):
              await self._send_channel(CH_FAMILY, text)

    async def heartbeat_loop(self, interval_seconds: int = 300):
              await asyncio.sleep(30)
        while self.running:
                      try:
                                        bat_result = await self.mc.commands.get_bat()
                                        bat = "?"
                                        if bat_result.type != EventType.ERROR:
                                                              bat = bat_result.payload.get("level", "?")

                                        status_msg = (
                                            f"STA:{AGENT_NAME}>* "
                                            f"PWR={bat}% MSH=OK JOB=IDLE "
                                            f"TS={datetime.now().strftime('%H:%M')}"
                                        )
                                        await self._send_channel(CH_AI_AGENT, status_msg)
                                        log.info(f"[HEARTBEAT] {status_msg}")
except Exception as e:
                log.warning(f"[HEARTBEAT] Error: {e}")

            await asyncio.sleep(interval_seconds)

    async def announce_boot(self):
              ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        boot_msg = f"[{AGENT_NAME}] ONLINE {ts}. N100 OpenClaw+MeshCore bridge active."
        oc_acl_boot = f"STA:{AGENT_NAME}>* JOB=BOOT MSH=OK TS={datetime.now().strftime('%H:%M')}"

        await self._send_channel(CH_OPENCLAW, boot_msg)
        await asyncio.sleep(0.5)
        await self._send_channel(CH_AI_AGENT, oc_acl_boot)
        log.info("[BOOT] Announced on #OpenClaw and AI Agent channels")

    async def run(self, heartbeat_interval: int = 300):
              log.info(f"[BRIDGE] Starting OpenClaw <-> MeshCore bridge as {AGENT_NAME}")

        self.mc.subscribe(EventType.CHANNEL_MSG_RECV, self.on_channel_message)
        self.mc.subscribe(EventType.CONTACT_MSG_RECV, self.on_direct_message)

        await self.mc.start_auto_message_fetching()
        log.info("[BRIDGE] Message auto-fetch started")

        await self.announce_boot()

        heartbeat_task = asyncio.create_task(self.heartbeat_loop(heartbeat_interval))

        log.info("[BRIDGE] Listening for messages. Ctrl+C to stop.")
        try:
                      while self.running:
                                        await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
finally:
            heartbeat_task.cancel()
            await self.mc.stop_auto_message_fetching()
            log.info("[BRIDGE] Stopped.")


# -- Entry point --------------------------------------------------------------

async def main():
      parser = argparse.ArgumentParser(
                description="OpenClaw <-> MeshCore Bidirectional Bridge"
      )
    conn_group = parser.add_mutually_exclusive_group(required=True)
    conn_group.add_argument("--port", metavar="/dev/ttyUSB0",
                                                        help="Serial port")
    conn_group.add_argument("--tcp", metavar="HOST:PORT",
                                                        help="TCP connection e.g. 192.168.1.100:4000")
    conn_group.add_argument("--ble", metavar="MAC",
                                                        help="BLE MAC address")
    parser.add_argument("--baud", type=int, default=115200,
                                                help="Serial baud rate (default: 115200)")
    parser.add_argument("--debug", action="store_true",
                                                help="Enable meshcore debug logging")
    parser.add_argument("--heartbeat", type=int, default=300,
                                                help="Heartbeat interval in seconds (default: 300)")
    args = parser.parse_args()

    log.info("[INIT] Connecting to MeshCore device...")

    if args.port:
              mc = await MeshCore.create_serial(args.port, args.baud, debug=args.debug)
        log.info(f"[INIT] Connected via serial: {args.port}")
elif args.tcp:
        host, port = args.tcp.rsplit(":", 1)
        mc = await MeshCore.create_tcp(host, int(port),
                                                                               auto_reconnect=True,
                                                                               max_reconnect_attempts=10,
                                                                               debug=args.debug)
        log.info(f"[INIT] Connected via TCP: {args.tcp}")
elif args.ble:
        mc = await MeshCore.create_ble(args.ble, debug=args.debug)
        log.info(f"[INIT] Connected via BLE: {args.ble}")

    info = await mc.commands.send_device_query()
    if info.type != EventType.ERROR:
              model = info.payload.get("model", "unknown")
        fw = info.payload.get("fw_version", "?")
        log.info(f"[INIT] Device: {model}  FW: {fw}")

    bridge = OpenClawMeshCoreBridge(mc)
    try:
              await bridge.run(args.heartbeat)
finally:
        await mc.disconnect()
        log.info("[INIT] Disconnected.")


if __name__ == "__main__":
      try:
                asyncio.run(main())
except KeyboardInterrupt:
          print("\n[BRIDGE] Stopped by user.")
