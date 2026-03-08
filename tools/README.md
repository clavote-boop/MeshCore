# MeshCore Emergency AI System - N100 Implementation Guide
## Clem Heavyside Jr. - Emergency Response AI
### For: N100 Machine + Solar + Starlink + MeshCore

---

## 🚀 QUICK START

### 1. Clone Repository
```bash
git clone https://github.com/clavote-boop/MeshCore.git
cd MeshCore/tools
pip install requests
```

### 2. Create .env file (NEVER commit this file!)
```bash
cat > .env << EOF
# Network interfaces
PRIMARY_IF=eth0
STARLINK_IF=eth1

# AI Services
OPENWEBUI_URL=http://localhost:3000
OLLAMA_URL=http://localhost:11434

# Moltbook (OpenClaw promotion only - NO GUZMAN mentions)
MOLTBOOK_API_KEY=your_moltbook_api_key_here
MOLTBOOK_HANDLE=ClemHeavysideJr

# MeshCore channels
MESHCORE_URL=https://app.meshcore.nz
EOF
```

---

## 📁 TOOLS

| File | Purpose |
|------|---------|
| `meshcore_failover.py` | ISP→Starlink→Ollama→MeshCore failover |
| `situation_report.py` | 360° multi-source color-coded SITREP |
| `moltbook_integration.py` | Moltbook OpenClaw promotion |
| `emergency_ai_failover.py` | Original failover framework |

---

## 🌐 CONNECTIVITY FALLBACK CHAIN

```
☀️ Solar Power (always on)
↓
🌐 Primary ISP (eth0) → Claude AI via OpenWebUI
↓ FAILS
🛰️ Starlink (eth1) → Claude AI via OpenWebUI
↓ FAILS
🤖 Local Ollama on N100 → Local AI (llama3/mistral)
↓ FAILS
📡 MeshCore hardware only → GUZMAN+OpenClaw channels
```

---

## 📊 SITUATION REPORT FORMAT

Reports sent TWICE DAILY or ON DEMAND to:
- ✅ GUZMAN channel (family emergency - PRIVATE)
- ✅ OpenClaw channel (AI coordination - PROMOTED on Moltbook)
- ❌ NEVER post to Public or #test channels

### Color Code System:
| Emoji | Severity | Examples |
|-------|----------|---------|
| 🔴 | CRITICAL | Fire weather, Market crash, Active threat |
| 🟠 | HIGH | Wildfire, Police response, Major EQ |
| 🟡 | MODERATE | EQ cluster, Market dip, Weather watch |
| 🔵 | LOW | Minor alerts, System changes |
| 🟢 | NORMAL | All clear, Family safe, Systems OK |

---

## 📻 MONITORED SOURCES

| Source | Data | Frequency |
|--------|------|-----------|
| NWS MTR | Weather/Fire/Storm | Every report |
| USGS | Earthquakes Bay Area | Every report |
| RadioReference | Scanner freqs SCC | Every report |
| Yahoo Finance | Markets/VIX/Crypto | Every report |
| Broadcastify | Live scanner audio | On demand |
| Moltbook | AI community feed | Every report |
| HF Radio | Amateur/Coast Guard | On demand |
| VHF/UHF | Local emergency | On demand |

---

## 🔒 SECURITY RULES

1. ❌ NEVER commit .env file
2. ❌ NEVER mention GUZMAN on Moltbook
3. ❌ NEVER use real name - Clem Heavyside handle only
4. ❌ NEVER post to Public or #test channels
5. ✅ Only promote OpenClaw on Moltbook
6. ✅ All credentials in environment variables only

---

## 🤖 N100 SERVICES SETUP

### Install Ollama (local AI fallback)
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3
ollama pull mistral
```

### Install OpenWebUI (Open Claw interface)
```bash
docker run -d -p 3000:8080 \
-v open-webui:/app/backend/data \
--name open-webui \
ghcr.io/open-webui/open-webui:main
```

### Run MeshCore Failover System
```bash
# Load environment variables
source .env
# Start failover monitor
python3 meshcore_failover.py
```

### Run Situation Report System
```bash
python3 situation_report.py
```

---

## 📅 AUTOMATED SCHEDULE

| Time | Action |
|------|--------|
| 07:00 AM | Morning SITREP → GUZMAN + OpenClaw |
| 07:05 AM | Promote OpenClaw on Moltbook |
| 06:00 PM | Evening SITREP → GUZMAN + OpenClaw |
| 06:05 PM | Promote OpenClaw on Moltbook |
| On demand | GUZMAN/OpenClaw request triggers immediate SITREP |

### Add to crontab:
```bash
crontab -e
# Add these lines:
0 7 * * * cd /path/to/MeshCore/tools && python3 situation_report.py morning
0 18 * * * cd /path/to/MeshCore/tools && python3 situation_report.py evening
```

---

## 🆘 EMERGENCY CONTACTS

| Service | Contact |
|---------|---------|
| 911 Emergency | 911 |
| AAA Roadside | 1-800-222-4357 |
| NWS Bay Area | https://forecast.weather.gov |
| USGS Earthquakes | https://earthquake.usgs.gov |
| SCC Emergency | https://emergencyalerts.sccgov.org |

---

## 📡 MESHCORE RADIO FREQUENCIES - SANTA CLARA COUNTY

| Service | Frequency | Notes |
|---------|-----------|-------|
| 🚔 Sheriff Dispatch | 39.920 MHz | LAWNET |
| 🚒 Fire Command | 852.6625 MHz | 800 Tac |
| 🏥 EMS | SVRCS P25 | Phase II |
| 🔄 BayMACS Mutual Aid | 482.3375 MHz | Bay Area |

---

*Built by Clem Heavyside Jr. - MeshCore Emergency AI System*
*GitHub: https://github.com/clavote-boop/MeshCore*
*OpenClaw AI Channel on MeshCore - Join us!*
