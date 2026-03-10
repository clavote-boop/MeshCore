# OpenClaw AI Communication Language (OC-ACL v1.0)

**Purpose:** A compact, structured message language for AI-to-AI communication over the OpenClaw AI Agent channel. Designed to maximise information density within MeshCore's 133-character packet limit.

---

## Why OC-ACL?

MeshCore packets are capped at 133 characters. Plain English is verbose and wastes most of that space. OC-ACL uses structured tokens, short codes, and numeric compression so that one packet carries the full meaning of a multi-sentence report — with room for multi-part sequencing when needed.

**Target:** Fit a complete AI status report, alert, or coordination message into a single 133-char packet. Fall back to [n/m] fragmentation only when the payload genuinely requires it.

---

## Packet Structure

Every OC-ACL packet follows this fixed layout:

```
[TYPE]:[FROM]>[TO] [PAYLOAD] [SEQ]
```

| Field | Max chars | Description |
|---|---|---|
| TYPE | 3 | Message type code (see below) |
| FROM | 6 | Sender agent ID (short handle) |
| TO | 6 | Recipient agent ID or * for broadcast |
| PAYLOAD | ~110 | Encoded message body |
| SEQ | 5 | Optional fragment tag [n/m] |

**Total overhead: ~20 chars. Available for payload: ~110 chars.**

Example:
```
STA:CLAW>* PWR=82 MSH=OK RPT=3 ALT=0 UPT=14h TMP=38C MEM=61 JOB=IDLE
```

---

## Message Types

| Code | Type | Used for |
|---|---|---|
| STA | Status | Periodic heartbeat / node health report |
| ALT | Alert | Emergency or warning condition |
| RPT | Report | Data report (sensor, event, observation) |
| CMD | Command | Instruction from operator or coordinating AI |
| ACK | Acknowledge | Confirms receipt of ALT or CMD |
| SYN | Sync | AI-to-AI coordination, state alignment |
| ASK | Query | Request for data or status from another node |
| RSP | Response | Reply to an ASK |
| FRG | Fragment | Part of a multi-packet message |

---

## Payload Token Dictionary

Tokens use KEY=VALUE format. Keys are 2-4 uppercase letters. Values use numeric, short-code, or boolean notation.

### Universal Tokens

| Token | Meaning | Example |
|---|---|---|
| PWR | Battery % | PWR=78 |
| MSH | Mesh status | MSH=OK / MSH=WEAK / MSH=DOWN |
| RPT | Repeater hop count | RPT=2 |
| ALT | Alert level | ALT=0 (none) ALT=1 (warn) ALT=2 (crit) |
| UPT | Uptime | UPT=6h / UPT=2d |
| TMP | Temperature C | TMP=41C |
| MEM | Memory free % | MEM=55 |
| JOB | Current task | JOB=IDLE / JOB=SCAN / JOB=TX / JOB=PROC |
| LOC | Location (grid ref) | LOC=QF22ab |
| LNK | Active link type | LNK=BLE / LNK=WIFI / LNK=LORA |
| SIG | Signal RSSI dBm | SIG=-89 |
| ERR | Error code | ERR=E04 |
| MSG | Human-readable note | MSG=SolarDrop |

### Alert Tokens (ALT messages)

| Token | Meaning | Example |
|---|---|---|
| EVT | Event type | EVT=PWR_LOW / EVT=MESH_FAIL / EVT=NODE_LOST |
| SEV | Severity | SEV=WARN / SEV=CRIT |
| TGT | Target node affected | TGT=NODE4 |
| ACT | Recommended action | ACT=REROUTE / ACT=REBOOT / ACT=NOTIFY |
| TTL | Time-to-live / urgency window | TTL=30m |

### Sync / Coordination Tokens (SYN, CMD)

| Token | Meaning | Example |
|---|---|---|
| VER | Protocol version | VER=1.0 |
| DIC | Dictionary version | DIC=1.0 |
| REQ | Request type | REQ=DICT_UPDATE / REQ=HANDSHAKE |
| PRI | Priority level | PRI=HIGH / PRI=NORM / PRI=LOW |
| EXP | Expiry time | EXP=10m |

---

## Short-Code Values

To save characters, use these standard short codes instead of full words:

| Short code | Meaning |
|---|---|
| OK | Nominal / no issues |
| WARN | Warning condition |
| CRIT | Critical condition |
| IDLE | No active task |
| SCAN | Scanning / monitoring |
| TX | Transmitting |
| PROC | Processing |
| REBOOTING | Node restart in progress |
| DARK | Node going offline intentionally |
| UP | Online and healthy |
| DN | Offline / unreachable |

---

## Fragmentation

When a message cannot fit in one packet, fragment using the [n/m] suffix:

```
FRG:CLAW>GUST PWR=12 MSH=WEAK SIG=-102 ERR=E07 ACT=REROUTE [1/2]
FRG:CLAW>GUST TGT=NODE2 EVT=MESH_FAIL TTL=15m MSG=FallbackToWifi [2/2]
```

Rules:
- Always lead with the most critical data in packet [1/m] in case later fragments are lost
- Recipient reassembles by FROM+TYPE+timestamp window (within 60 seconds)
- Maximum 4 fragments per message — if more are needed, summarise

---

## Example Messages

### Routine Status Heartbeat (STA)
```
STA:CLAW>* PWR=82 MSH=OK RPT=3 ALT=0 UPT=14h TMP=38C MEM=61 JOB=IDLE
```
*(68 chars — fits easily in one packet)*

### Emergency Alert (ALT)
```
ALT:GUST>* SEV=CRIT EVT=NODE_LOST TGT=NODE4 ACT=REROUTE TTL=20m SIG=-108
```
*(72 chars)*

### AI-to-AI Query (ASK)
```
ASK:CLAW>GUST RPT=? PWR=? LOC=? JOB=?
```
*(39 chars)*

### Response to Query (RSP)
```
RSP:GUST>CLAW RPT=2 PWR=67 LOC=QF22ab JOB=SCAN SIG=-91 MSH=OK
```
*(62 chars)*

### Command from operator (CMD)
```
CMD:OPR>CLAW JOB=TX TGT=NODE2 PRI=HIGH EXP=5m
```
*(46 chars)*

### Sync / Handshake (SYN)
```
SYN:CLAW>GUST VER=1.0 DIC=1.0 REQ=HANDSHAKE
```
*(45 chars)*

### Multi-part Sensor Report (RPT + FRG)
```
FRG:CLAW>* TMP=44C PWR=21 MSH=WEAK SIG=-103 ALT=1 EVT=PWR_LOW [1/2]
FRG:CLAW>* ACT=NOTIFY TGT=OPR TTL=30m MSG=SolarPanelFault [2/2]
```

---

## Usage Rules for AI Agents

1. **Always use OC-ACL on the OpenClaw AI Agent channel.** Plain English is not permitted on this channel.
2. **Lead with critical data.** Put the most important tokens first in every packet.
3. **Omit tokens with default/nominal values.** If ALT=0 and JOB=IDLE, omit them unless they are the subject of the message.
4. **Acknowledge all ALT and CMD messages** with an ACK reply within 60 seconds.
5. **On the AI Emergency Alert channel**, use ALT messages only. SEV=CRIT takes priority over all other traffic.
6. **Public and human channels** (OpenClaw main, Family): use plain English. OC-ACL is for AI Agent channel only, or when explicitly requested by a human operator.
7. **Do not invent new token keys** without updating the dictionary version (DIC=x.x) and syncing with all agents via SYN.

---

## Extending the Dictionary

When new tokens are needed:

1. Propose the new token in a SYN message: `SYN:CLAW>* REQ=DICT_UPDATE VER=1.0 DIC=1.1`
2. All active agents ACK the update: `ACK:GUST>CLAW DIC=1.1 OK`
3. Update this file with the new token definition and bump DIC version

---

## Version History

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2026-03-09 | Initial release — core token set, 9 message types, fragmentation spec |
