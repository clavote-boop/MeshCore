#!/usr/bin/env python3
# ============================================================
# Dynamic Multi-Source Situation Report System
# Clem Heavyside Jr. - MeshCore Emergency Response
# Color coded: 🔴RED=Critical 🟡YELLOW=Warning 🟢GREEN=Normal
# Posts to GUZMAN + OpenClaw channels ONLY
# ============================================================
import os, json, time
from datetime import datetime
from collections import defaultdict

# SEVERITY LEVELS with emoji color codes
SEVERITY = {
  "CRITICAL": {"emoji": "🔴", "priority": 5},
  "HIGH":     {"emoji": "🟠", "priority": 4},
  "MODERATE": {"emoji": "🟡", "priority": 3},
  "LOW":      {"emoji": "🔵", "priority": 2},
  "NORMAL":   {"emoji": "🟢", "priority": 1},
}

# SOURCES being monitored
SOURCES = [
  "USGS",        # Earthquake/geological
  "NWS",         # National Weather Service
  "POLICE",      # Law enforcement
  "FIRE",        # Fire department
  "EMS",         # Emergency medical
  "MILITARY",    # National Guard/Military
  "COAST_GUARD", # Coast Guard/Maritime
  "HF_RADIO",    # HF amateur radio traffic
  "VHF_UHF",     # VHF/UHF local radio
  "STARLINK",    # Starlink connectivity
  "MESHCORE",    # MeshCore mesh network
  "FAMILY",      # Family member check-ins
]

# Active issues tracker - dynamic multi-source
issues = defaultdict(list)

def add_issue(source, severity, description, location=""):
  """Add or update an issue from a source"""
  issue = {
  "id": f"{source}-{int(time.time())}",
  "source": source,
  "severity": severity,
  "emoji": SEVERITY[severity]["emoji"],
  "priority": SEVERITY[severity]["priority"],
  "description": description,
  "location": location,
  "timestamp": datetime.now().strftime("%H:%M"),
  "active": True
  }
  issues[source].append(issue)
  return issue

def resolve_issue(source, issue_id):
  """Mark an issue as resolved"""
  for issue in issues[source]:
    if issue["id"] == issue_id:
      issue["active"] = False
      issue["resolved_at"] = datetime.now().strftime("%H:%M")
      return issues[source]

def get_active_issues():
  """Get all active issues sorted by priority (highest first)"""
  active = []
  for source_issues in issues.values():
    active.extend([i for i in source_issues if i["active"]])
    return sorted(active, key=lambda x: x["priority"], reverse=True)

def build_sitrep():
  """Build multi-part situation report with color coding"""
  active = get_active_issues()
  now = datetime.now().strftime("%Y-%m-%d %H:%M")

if not active:
  return [f"[SITREP] 🟢 {now} Clem Heavyside Jr. ALL CLEAR. No active issues. All sources nominal. GUZMAN+OpenClaw monitored. 📡"]

# Build report parts (max 133 chars each for MeshCore)
parts = []
header = f"[SITREP {now}] {len(active)} ACTIVE ISSUES:"
parts.append(header)

for i, issue in enumerate(active):
  line = (
    f"{issue['emoji']} [{issue['source']}] "
    f"{issue['severity']}: {issue['description']}"
    f"{' @'+issue['location'] if issue['location'] else ''}"
    f" ({issue['timestamp']})"
  )
  parts.append(line)

return parts

def format_meshcore_messages(parts):
  """Split report into 133-char MeshCore messages with part numbers"""
  messages = []
  total = len(parts)
  for i, part in enumerate(parts):
    prefix = f"[P{i+1}/{total}] " if total > 1 else ""
    # Truncate to 133 chars
    msg = f"{prefix}{part}"[:133]
    messages.append(msg)
    return messages

def send_sitrep_to_channels(messages):
  """Send situation report to GUZMAN and OpenClaw ONLY"""
  print(f"\n{'='*60}")
  print(f"SITUATION REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
  print(f"Sending to: GUZMAN + OpenClaw ONLY")
  print(f"{'='*60}")
  for msg in messages:
    print(f"📡 {msg}")
    print(f"{'='*60}\n")
    # TODO: Wire up MeshCore BLE companion protocol
    # guzman_channel.send(msg)
    # openclaw_channel.send(msg)

if __name__ == "__main__":
  # Example: simulate multiple sources reporting issues
  print("[BOOT] Dynamic Multi-Source Situation Report System")
  print("[INFO] Clem Heavyside Jr. - MeshCore Emergency Response")

# Simulate incoming reports from multiple sources
add_issue("USGS", "CRITICAL", "7.7 EQ off Yreka coast", "Yreka CA")
add_issue("NWS", "CRITICAL", "Tsunami warning 15-25ft", "Coastal CA")
add_issue("FIRE", "HIGH", "Wildfire Yreka National Forest", "North CA")
add_issue("POLICE", "HIGH", "Evacuation order issued", "Coastal zones")
add_issue("EMS", "MODERATE", "Field hospitals active", "Shasta Valley")
add_issue("MILITARY", "MODERATE", "National Guard deployed", "Yreka CA")
add_issue("STARLINK", "LOW", "ISP down Starlink active", "Home base")
add_issue("FAMILY", "NORMAL", "All family checked in safe", "Inland")

# Build and send situation report
parts = build_sitrep()
messages = format_meshcore_messages(parts)
send_sitrep_to_channels(messages)
print(f"[DONE] {len(messages)} messages ready for GUZMAN+OpenClaw")
