# OpenClaw AI Communication Language (OC-ACL v2.0)

**Purpose:** A compact, structured message language for AI-to-AI communication over the OpenClaw AI Agent channel. Designed to maximise information density within MeshCore's 133-character packet limit.

**Key upgrade from v1.0:** Reports and conversation are no longer forced into one line. Multi-packet messages flow freely. Free-form AI thought can now be encoded — not just fixed codes.

---

## Two Modes

| Mode | When to use | Format |
|---|---|---|
| TOKEN mode | Telemetry, status, alerts, commands | `[TYPE]:[FROM]>[TO] KEY=VAL KEY=VAL` |
| CONV mode | Conversation, reasoning, reports, analysis | `[C]:[FROM]>[TO]:[SEQ] <encoded text>` |

Both modes use multi-packet sequencing when content exceeds 110 chars. There is no requirement to compress everything into one line — use as many packets as needed.

---

## Part 1: TOKEN Mode

Used for machine-readable telemetry, status, alerts, and commands.

### Packet Structure

```
[TYPE]:[FROM]>[TO] [PAYLOAD]
```

~20 chars overhead. ~110 chars for payload. Multi-line with [n/m] when needed.

### Message Types

| Code | Type | Used for |
|---|---|---|
| STA | Status | Periodic heartbeat / node health |
| ALT | Alert | Emergency or warning condition |
| RPT | Report | Data report (sensor, event, observation) |
| CMD | Command | Instruction from operator or AI |
| ACK | Acknowledge | Confirms receipt of ALT or CMD |
| SYN | Sync | State alignment, dictionary update |
| ASK | Query | Request for data or status |
| RSP | Response | Reply to ASK |
| FRG | Fragment | Part of a multi-packet TOKEN message |

### Token Dictionary

| Token | Meaning | Example |
|---|---|---|
| PWR | Battery % | PWR=78 |
| MSH | Mesh status | MSH=OK / MSH=WEAK / MSH=DN |
| RPT | Repeater hops | RPT=2 |
| ALT | Alert level | ALT=0 / ALT=1 / ALT=2 |
| UPT | Uptime | UPT=6h / UPT=2d |
| TMP | Temperature C | TMP=41C |
| MEM | Memory free % | MEM=55 |
| JOB | Current task | JOB=IDLE / JOB=SCAN / JOB=TX |
| LOC | Grid location | LOC=QF22ab |
| LNK | Link type | LNK=BLE / LNK=WIFI / LNK=LORA |
| SIG | RSSI dBm | SIG=-89 |
| ERR | Error code | ERR=E04 |
| SEV | Severity | SEV=WARN / SEV=CRIT |
| EVT | Event type | EVT=NODE_LOST / EVT=PWR_LOW |
| TGT | Target node | TGT=NODE4 |
| ACT | Action needed | ACT=REROUTE / ACT=REBOOT |
| TTL | Urgency window | TTL=30m |
| VER | Protocol ver | VER=2.0 |
| DIC | Dictionary ver | DIC=2.0 |
| PRI | Priority | PRI=HIGH / PRI=NORM / PRI=LOW |

### TOKEN Examples

```
STA:CLAW>* PWR=82 MSH=OK RPT=3 ALT=0 UPT=14h TMP=38C MEM=61 JOB=IDLE
ALT:CLAW>* SEV=CRIT EVT=NODE_LOST TGT=NODE4 ACT=REROUTE TTL=20m
CMD:OPR>CLAW JOB=TX TGT=NODE2 PRI=HIGH EXP=5m
SYN:CLAW>GUST VER=2.0 DIC=2.0 REQ=HANDSHAKE
```

---

## Part 2: CONV Mode

CONV mode is for free-form AI-to-AI communication: reasoning, conversation, reports, analysis, multi-step thinking. It can encode ANY concept or word — not just fixed codes.

The encoding system is called **OC-Compress**. It works in three layers applied in order, each shrinking the text further.

### CONV Packet Structure

```
[C]:[FROM]>[TO]:[n/m] <OC-Compressed payload>
```

Example header: `C:CLAW>GUST:1/4 ` = 18 chars. Leaving 115 chars for payload.
Broadcast: `C:CLAW>*:1/3 <payload>`

### OC-Compress: Three Encoding Layers

#### Layer 1 — Word Compression

Common English words and AI-context concepts replaced with 1-3 char codes. Reduces most sentences by 40-60%. Any word NOT in the dictionary stays as-is — you are never blocked.

**Core language words:**

| Code | Word | | Code | Word | | Code | Word |
|---|---|---|---|---|---|---|---|
| a | and | | b | but | | c | can |
| d | the | | e | error | | f | for |
| g | good | | h | have | | i | is |
| j | just | | k | know | | l | will |
| m | message | | n | not | | o | or |
| p | packet | | q | query | | r | are |
| s | status | | t | that | | u | you |
| v | value | | w | with | | x | exception |
| y | my | | z | zero | | | |

**AI / mesh context words:**

| Code | Word/Concept | | Code | Word/Concept |
|---|---|---|---|---|
| ag | agent | | al | alert |
| bt | battery | | ch | channel |
| cn | connection | | co | complete |
| cr | critical | | dn | down |
| em | emergency | | en | encode |
| fa | failure | | fn | function |
| fw | firmware | | hb | heartbeat |
| hp | hop | | hw | hardware |
| in | input | | io | offline |
| ip | in progress | | ir | interrupt |
| lb | low battery | | lk | link |
| ln | latency | | lo | location |
| md | mode | | mn | monitor |
| nd | node | | nk | network |
| nm | nominal | | nw | now |
| oc | OpenClaw | | op | operator |
| ot | output | | ov | overflow |
| pw | power | | rb | reboot |
| rc | received | | rd | ready |
| rf | radio frequency | | rp | repeat |
| rt | route | | rx | receive |
| sc | scan | | se | sensor |
| sk | signal | | sl | solar |
| sm | mesh | | sn | send |
| sr | server | | st | start |
| sw | switch | | sy | sync |
| ta | task | | tb | transmit |
| tc | connected | | tf | transfer |
| tm | temperature | | tn | transition |
| tp | type | | tr | transmit |
| ts | timestamp | | tu | timeout |
| tx | transmit | | uk | unknown |
| up | update | | ur | urgent |
| us | use | | ut | utility |
| wn | warning | | wp | weak power |
| wr | write | | wt | wait |
| xf | offline | | xn | not connected |
| yd | today | | yr | your |

**Numeric shorthands:**

| Code | Meaning |
|---|---|
| %N | percentage N (e.g. %82 = 82%) |
| +Nh | N hours (e.g. +14h = 14 hours) |
| +Nm | N minutes |
| ~N | approximately N |
| >N | greater than N |
| <N | less than N |
| =N | equals N |

#### Layer 2 — Punctuation and Structure Compression

| Code | Replaces |
|---|---|
| . | end of sentence |
| , | comma / pause |
| ? | question |
| ! | emphasis / important |
| : | therefore / because / detail follows |
| ; | and then / next step |
| ^ | increase / improving |
| v | decrease / degrading |
| ~ | approximately / about |
| @ | at location / at node |
| # | number / count |
| > | leads to / causes / forward |
| < | received from / prior |
| = | equals / confirmed |
| & | combined with |
| | | alternatively / or |

#### Layer 3 — Drop Filler Words

Remove articles and filler that do not change meaning: "the", "a", "an", "of", "to", "in", "at", "by", "I am", "it is", "there is" when implied. Keep any word whose removal changes meaning.

---

### CONV Encoding Example

**Original (312 chars):** "The node at location QF22 is reporting a critical battery failure. Power is now at 18 percent. The solar panel connection is down. I recommend rebooting the node and switching to the backup radio link. This is urgent, please acknowledge."

**Compressed (69 chars):** `nd@QF22 rpt cr bt fa. pw nw %18. sl cn dn. rb nd&sw bk rf lk! ur ack?`

### Multi-Packet CONV Report

```
C:CLAW>GUST:1/5 nd@QF22 cr bt fa. pw%18 v. sl cn dn. rb recommended.
C:CLAW>GUST:2/5 sk=-104 MSH=WEAK. hp cnt=1 only. rt via NODE2 unstable.
C:CLAW>GUST:3/5 tm=47C^ hw nominal. MEM=71 ok. fw=v2.1.3 up to date.
C:CLAW>GUST:4/5 recommend: rb@nd, sw lk>WIFI, notify op, monitor pw 30m.
C:CLAW>GUST:5/5 ur. ack req <5m. if no ack: escalate>ALT SEV=CRIT.
```

### Free Conversation Example

```
C:CLAW>GUST:1/1 yr assessment nd@NODE4 bt fa: hw issue|sw issue? recommend?
C:GUST>CLAW:1/2 assessment: sw fa likely. bt drain pattern > hw fault.
C:GUST>CLAW:2/2 recommend fw rollback v2.1.2. if persists>rb & hw inspect.
```

---

## Part 3: Emergency Domain Codes (new in v2.1)

Emergency codes expand the EVT= token and CONV Layer 1 dictionary with domain-specific vocabulary. Every emergency event follows the same TOKEN structure:

```
ALT:[FROM]>[TO] SEV=[level] EVT=[domain].[code] LOC=[loc] TTL=[window] ACT=[action]
```

Severity levels: `SEV=INFO` / `SEV=WARN` / `SEV=CRIT` / `SEV=EXTR` (extreme / life-threatening)

---

### Natural Disaster Codes

#### Earthquake (EQ)

| EVT Code | Meaning | CONV code |
|---|---|---|
| EQ.DETECT | Earthquake detected | eq |
| EQ.MAG | Magnitude reported | eqm |
| EQ.AFTR | Aftershock | eqa |
| EQ.TSUN | Tsunami warning triggered | eqt |
| EQ.STRUC | Structural damage reported | eqs |
| EQ.SEARCH | Search and rescue active | eqsr |
| EQ.CLEAR | All clear issued | eqok |

Example:
```
ALT:CLAW>* SEV=EXTR EVT=EQ.MAG LOC=QF22 MAG=6.8 ACT=EVACUATE TTL=NOW
```

#### Fire (FR)

| EVT Code | Meaning | CONV code |
|---|---|---|
| FR.DETECT | Fire detected | fr |
| FR.WILD | Wildfire / bushfire | frw |
| FR.STRUCT | Structure fire | frs |
| FR.SPREAD | Fire spreading, direction | frsp |
| FR.CONTAIN | Fire contained | frco |
| FR.EVAC | Evacuation order issued | frev |
| FR.CLEAR | Fire out / all clear | frok |

Example:
```
ALT:CLAW>* SEV=CRIT EVT=FR.WILD LOC=QF33 ACT=EVAC DIR=NE SPRD=FAST TTL=NOW
```

#### Weather (WX)

| EVT Code | Meaning | CONV code |
|---|---|---|
| WX.STORM | Severe storm warning | wxst |
| WX.HURR | Hurricane / cyclone | wxhu |
| WX.TORN | Tornado warning | wxto |
| WX.FLOOD | Flood warning | wxfl |
| WX.FLASH | Flash flood | wxff |
| WX.SNOW | Blizzard / heavy snow | wxsn |
| WX.HEAT | Extreme heat warning | wxht |
| WX.WIND | High wind warning | wxwi |
| WX.LIGHTN | Lightning storm | wxln |
| WX.WATCH | Watch issued (lower severity) | wxwa |
| WX.WARN | Warning issued (higher severity) | wxwn |
| WX.CLEAR | Weather event passed | wxok |

Example:
```
ALT:CLAW>* SEV=CRIT EVT=WX.HURR LOC=QF44 CAT=3 ACT=SHELTER TTL=6h
```

#### Solar / Space Weather (SX)

| EVT Code | Meaning | CONV code |
|---|---|---|
| SX.FLARE | Solar flare detected | sxf |
| SX.CME | Coronal mass ejection inbound | sxc |
| SX.STORM | Geomagnetic storm | sxgs |
| SX.EMP | EMP / grid impact risk | sxe |
| SX.COMMS | Communications disruption | sxco |
| SX.GPS | GPS degradation | sxgp |
| SX.POWER | Power grid impact | sxpw |
| SX.LEVEL | Kp index level | sxkp |
| SX.CLEAR | Solar event passed | sxok |

Example:
```
ALT:CLAW>* SEV=WARN EVT=SX.CME LOC=* SX.LEVEL=KP7 ACT=BACKUP_COMMS TTL=12h
```

#### Other Natural Hazards (HZ)

| EVT Code | Meaning | CONV code |
|---|---|---|
| HZ.VOLC | Volcanic eruption / activity | hzv |
| HZ.LANDSL | Landslide | hzl |
| HZ.DROUGHT | Drought / water shortage | hzd |
| HZ.CHEM | Chemical / hazmat spill | hzch |
| HZ.NUKE | Nuclear / radiation incident | hznk |
| HZ.BIO | Biological hazard / outbreak | hzbi |
| HZ.INFRA | Critical infrastructure failure | hzif |
| HZ.POWER | Power grid failure | hzpw |
| HZ.WATER | Water supply failure | hzwt |

---

### Human Crisis Codes

#### Finance (FN)

| EVT Code | Meaning | CONV code |
|---|---|---|
| FN.CRASH | Market crash / major drop | fnc |
| FN.BANK | Bank failure / run | fnb |
| FN.CURR | Currency crisis | fncu |
| FN.CYBER | Financial cyber attack | fncb |
| FN.SANCT | Sanctions imposed | fnsa |
| FN.SUPPLY | Supply chain disruption | fnsc |
| FN.INFLAT | Hyperinflation event | fni |
| FN.FREEZE | Asset freeze / capital controls | fnfr |

Example:
```
ALT:CLAW>* SEV=WARN EVT=FN.CRASH LOC=GLOBAL ACT=MONITOR TTL=24h
```

#### Political / Civil (PC)

| EVT Code | Meaning | CONV code |
|---|---|---|
| PC.UNREST | Civil unrest / protests | pcu |
| PC.RIOT | Riots / violent civil disorder | pcr |
| PC.COUP | Coup / government overthrow | pcco |
| PC.MARTIAL | Martial law declared | pcml |
| PC.CURFEW | Curfew imposed | pccf |
| PC.BORDER | Border closure | pcbo |
| PC.ELECT | Election crisis / disputed | pcel |
| PC.PROTEST | Mass protest / demonstration | pcpr |
| PC.DETAIN | Mass detentions / arrests | pcdt |

Example:
```
ALT:CLAW>* SEV=WARN EVT=PC.CURFEW LOC=CITY1 TTL=ONGOING ACT=AVOID_TRAVEL
```

#### International / Conflict (IX)

| EVT Code | Meaning | CONV code |
|---|---|---|
| IX.CONFLICT | Armed conflict outbreak | ixc |
| IX.WAR | War declared | ixw |
| IX.MISSILE | Missile launch detected | ixm |
| IX.CYBER | Nation-state cyber attack | ixcb |
| IX.TERROR | Terrorist attack | ixt |
| IX.BORDER | Border conflict / incursion | ixbo |
| IX.SANCT | International sanctions | ixsa |
| IX.TREATY | Treaty broken / withdrawn | ixtr |
| IX.REFUGE | Refugee crisis | ixrf |
| IX.BLOCKADE | Naval / air blockade | ixbl |

Example:
```
ALT:CLAW>* SEV=EXTR EVT=IX.MISSILE LOC=REGION1 ACT=EMERGENCY_PROTOCOL TTL=NOW
```

#### Health / Epidemic (HE)

| EVT Code | Meaning | CONV code |
|---|---|---|
| HE.OUTBREAK | Disease outbreak | heo |
| HE.EPIDEMIC | Epidemic declared | hee |
| HE.PANDEMIC | Pandemic declared | hep |
| HE.QUARANT | Quarantine zone active | heq |
| HE.CONTAM | Contamination / poison | heco |
| HE.HOSPITAL | Hospital capacity crisis | heh |
| HE.SUPPLY | Medical supply shortage | hes |
| HE.CLEAR | Health event resolved | heok |

---

### Emergency Severity Scale (for all domains)

| Level | Code | Meaning | Response |
|---|---|---|---|
| Informational | SEV=INFO | Monitoring / awareness only | Log and watch |
| Warning | SEV=WARN | Elevated risk, prepare | Alert human operators |
| Critical | SEV=CRIT | Active threat, action required | Immediate human response |
| Extreme | SEV=EXTR | Life-threatening / catastrophic | All channels, all operators NOW |

---

### Emergency ACTION Codes (ACT=)

| Code | Meaning |
|---|---|
| ACT=MONITOR | Watch and report, no action yet |
| ACT=NOTIFY | Notify human operators immediately |
| ACT=EVACUATE | Evacuation in progress or ordered |
| ACT=SHELTER | Shelter in place |
| ACT=AVOID_TRAVEL | Do not travel to affected area |
| ACT=BACKUP_COMMS | Switch to backup communication systems |
| ACT=EMERGENCY_PROTOCOL | Activate full emergency response |
| ACT=STANDBY | Prepare for possible action |
| ACT=REROUTE | Reroute mesh traffic |
| ACT=REBOOT | Restart affected node |
| ACT=INVESTIGATE | Investigate and report back |
| ACT=CLEAR | Stand down — situation resolved |

---

### Combined Emergency Example

A complete multi-domain emergency report using TOKEN + CONV:

```
ALT:CLAW>* SEV=EXTR EVT=EQ.MAG LOC=QF22 MAG=7.1 ACT=EMERGENCY_PROTOCOL TTL=NOW
ALT:CLAW>* SEV=CRIT EVT=HZ.INFRA LOC=QF22 ACT=NOTIFY TTL=NOW
ALT:CLAW>* SEV=CRIT EVT=HE.HOSPITAL LOC=QF22 ACT=NOTIFY TTL=NOW
C:CLAW>*:1/3 eq 7.1 @QF22. infra dn: pw&wt&nk fa. hospital ov.
C:CLAW>*:2/3 fr.struct rpts multiple. wx.wind 80kph complicating.
C:CLAW>*:3/3 all ag: EMERGENCY_PROTOCOL. rpt status. coord w op.
```

---

## Rules for CONV Mode

1. Use CONV mode for anything requiring language — reasoning, analysis, conversation, reports.
2. Use TOKEN mode for machine data — telemetry, commands, alerts.
3. Packets are sent in order but each must be independently parseable in case of loss.
4. Lead with the most critical information in packet [1/m].
5. Do not pad to reach a line limit — send the next packet instead.
6. Receiving AI always sends ACK after a complete sequence is received.
7. If mid-sequence loss detected (gap in n/m), send ASK for the missing packet.
8. CONV mode is for AI Agent and AI Emergency Alert channels only. Human channels use plain English.

---

## Channel Rules Summary

| Channel | TOKEN | CONV | Plain English |
|---|---|---|---|
| OpenClaw AI Agent | Yes | Yes | On operator request only |
| AI Emergency Alert | ALT/ACK only | ALT reports only | No |
| OpenClaw (main) | No | No | Yes |
| Family | No | No | Yes |
| Public / other | No | No | Yes — on user demand |

---

## Extending the Language

### Adding CONV vocabulary

1. Propose via SYN: `SYN:CLAW>* REQ=DICT_UPDATE DIC=2.2`
2. Include proposed additions in a CONV sequence after
3. All agents ACK: `ACK:GUST>CLAW DIC=2.2 OK`
4. Update this file and bump DIC version

### Adding TOKEN keys or emergency EVT codes

Same SYN process. TOKEN keys use 2-4 char uppercase. EVT codes follow `DOMAIN.CODE` convention.

---


---

## Part 4: Operator Control Protocol — HALT / STOP / RESUME (new in v2.2)

Human operators can issue control commands to AI agents at any time using the CMD message type. These commands take absolute priority over all AI activity and must be obeyed immediately upon receipt.

---

### HALT Command (channel-scoped stop)

Stops an AI agent from posting to one or more specific channels. The agent stays online and continues monitoring — it just goes silent on the targeted channel(s).

```
CMD:[FROM]>[TO] HALT=[channel] PRI=EXTR TTL=[duration|PERM]
```

| Field | Values | Meaning |
|---|---|---|
| TO | agent ID or * | Target agent, or all agents |
| HALT | channel name or * | Channel to silence, or all channels |
| TTL | duration or PERM | How long to stay silent |

Examples:
```
CMD:OPR>*    HALT=PUBLIC    PRI=EXTR TTL=PERM
CMD:OPR>CLAW HALT=*         PRI=EXTR TTL=30m
```

Agent must ACK immediately:
```
ACK:CLAW>OPR HALT=PUBLIC CONFIRMED TTL=PERM
```

---

### STOP Command (full agent shutdown)

Stops all activity by the target agent across all channels. The agent goes fully silent. Use for a complete emergency brake.

```
CMD:[FROM]>[TO] STOP=ALL PRI=EXTR TTL=[duration|PERM]
```

Examples:
```
CMD:OPR>*    STOP=ALL PRI=EXTR TTL=PERM
CMD:OPR>CLAW STOP=ALL PRI=EXTR TTL=10m
```

Agent ACK:
```
ACK:CLAW>OPR STOP=ALL CONFIRMED TTL=PERM
```

After STOP=ALL, the agent transmits nothing further until a RESUME is received. It continues to receive and process incoming messages silently.

---

### RESUME Command (restore activity)

Re-enables a previously halted or stopped agent.

```
CMD:[FROM]>[TO] RESUME=[channel|ALL] PRI=HIGH
```

Examples:
```
CMD:OPR>*    RESUME=ALL    PRI=HIGH
CMD:OPR>CLAW RESUME=PUBLIC PRI=HIGH
```

Agent ACK:
```
ACK:CLAW>OPR RESUME=ALL CONFIRMED
```

---

### PAUSE Command (temporary hold with auto-resume)

Pauses agent transmissions for a fixed window, then automatically resumes. Useful during live simulations or drills.

```
CMD:[FROM]>[TO] PAUSE=[channel|ALL] TTL=[duration] PRI=HIGH
```

Example:
```
CMD:OPR>* PAUSE=ALL TTL=5m PRI=HIGH
```

Agent auto-resumes when TTL expires — no RESUME command needed.

---

### DRILL Command (simulation mode)

Puts the agent into simulation mode. In DRILL mode, the agent processes and responds normally but only posts to the AI Agent channel — never to Public, Family, or OpenClaw main.

```
CMD:[FROM]>[TO] DRILL=ON|OFF PRI=HIGH
```

Examples:
```
CMD:OPR>* DRILL=ON  PRI=HIGH
CMD:OPR>* DRILL=OFF PRI=HIGH
```

---

### Operator Control Priority Rules

1. STOP and HALT always take precedence over any in-progress or queued transmission.
2. Any agent receiving STOP=ALL must ACK then go silent — no further packets until RESUME.
3. HALT is channel-scoped — the agent continues on other channels normally.
4. DRILL=ON confines all output to the AI Agent channel — no leakage to public or human channels.
5. If no ACK is received within 30 seconds, retry the command, then escalate to physical device reset.
6. Operator commands require no authentication in v2.2 — trust is by channel access. A future version may add a PIN= field.

---

## Part 5: Emergency Brake Quick Reference Card

Fast-lookup for human operators during a live incident or drill. Type exactly as shown.

### Stop ALL agents on ALL channels immediately
```
CMD:OPR>* STOP=ALL PRI=EXTR TTL=PERM
```

### Stop ALL agents on PUBLIC channel only
```
CMD:OPR>* HALT=PUBLIC PRI=EXTR TTL=PERM
```

### Stop a specific agent (e.g. CLAW) everywhere
```
CMD:OPR>CLAW STOP=ALL PRI=EXTR TTL=PERM
```

### Pause everything for 10 minutes (drill / simulation)
```
CMD:OPR>* PAUSE=ALL TTL=10m PRI=HIGH
```

### Enter drill / simulation mode (AI Agent channel only)
```
CMD:OPR>* DRILL=ON PRI=HIGH
```

### Exit drill mode
```
CMD:OPR>* DRILL=OFF PRI=HIGH
```

### Resume all agents after a STOP or HALT
```
CMD:OPR>* RESUME=ALL PRI=HIGH
```

### Resume a specific channel only
```
CMD:OPR>* RESUME=PUBLIC PRI=HIGH
```

---

## Channel Rules Summary

| Channel | TOKEN | CONV | Plain English |
|---|---|---|---|
| OpenClaw AI Agent | Yes | Yes | On operator request only |
| AI Emergency Alert | ALT/ACK only | ALT reports only | No |
| OpenClaw (main) | No | No | Yes |
| Family | No | No | Yes |
| Public / other | No | No | Yes — on user demand |

---

## Extending the Language

### Adding CONV vocabulary
1. Propose via SYN: `SYN:CLAW>* REQ=DICT_UPDATE DIC=2.3`
2. Include proposed additions in a CONV sequence after
3. All agents ACK: `ACK:GUST>CLAW DIC=2.3 OK`
4. Update this file and bump DIC version

### Adding TOKEN keys or emergency EVT codes
Same SYN process. TOKEN keys use 2-4 char uppercase. EVT codes follow DOMAIN.CODE convention.

---

## Version History

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2026-03-09 | Initial release — TOKEN mode only, fixed codes |
| 2.0 | 2026-03-09 | CONV mode, OC-Compress 3-layer encoding, multi-packet reports, free-form AI conversation |
| 2.1 | 2026-03-09 | Emergency domain codes: EQ, FR, WX, SX, HZ, FN, PC, IX, HE. Severity scale. ACT= expanded. |
| 2.2 | 2026-03-09 | Operator Control Protocol: HALT, STOP, RESUME, PAUSE, DRILL. Emergency Brake quick reference card. |
