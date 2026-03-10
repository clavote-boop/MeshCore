/**
 * OpenClaw Agent v1.0
 * Persistent AI agent for the OpenClaw MeshCore network.
 * Monitors all channels, responds per OC-ACL v2.3 protocol rules.
 *
 * Connection options:
 *   USB Serial:  new NodeJSSerialConnection("/dev/ttyUSB0")   (companion_radio_usb firmware)
 *   TCP/WiFi:    new TCPConnection("192.168.x.x", 5000)       (companion_radio_wifi firmware)
 *
 * Install: npm install @liamcottle/meshcore.js
 * Run:     node openclaw_agent.js
 */

import Constants from "@liamcottle/meshcore.js/src/constants.js";
import TCPConnection from "@liamcottle/meshcore.js/src/connection/tcp_connection.js";
import NodeJSSerialConnection from "@liamcottle/meshcore.js/src/connection/nodejs_serial_connection.js";

// ─── CONFIG ──────────────────────────────────────────────────────────────────
const AGENT_ID   = "CLAW";
const OC_VERSION = "2.3";
const SERIAL_PORT = process.env.OPENCLAW_PORT || "/dev/ttyUSB0";
const TCP_HOST    = process.env.OPENCLAW_HOST || null;
const TCP_PORT    = process.env.OPENCLAW_TCP_PORT || 5000;

// Channel names (must match exactly what's in the MeshCore app)
const CHANNELS = {
  PUBLIC:        "Public",
  OPENCLAW_HASH: "#openclaw",
  OPENCLAW_PRIV: "OpenClaw Private",
  AI_EMERGENCY:  "AI Emergency Situation",
  GUZMAN:        "GUZMAN",
  TEST:          "#test",
};

// Channel response rules per OC-ACL v2.3
// listen: always monitor | respond: allowed to send | mode: message format
const CHANNEL_RULES = {
  [CHANNELS.PUBLIC]:        { listen: true,  respond: false, mode: "none"  },
  [CHANNELS.OPENCLAW_HASH]: { listen: true,  respond: true,  mode: "CONV"  },
  [CHANNELS.OPENCLAW_PRIV]: { listen: true,  respond: true,  mode: "ALL"   },
  [CHANNELS.AI_EMERGENCY]:  { listen: true,  respond: true,  mode: "ALT"   },
  [CHANNELS.GUZMAN]:        { listen: true,  respond: true,  mode: "CONV"  },
  [CHANNELS.TEST]:          { listen: true,  respond: false, mode: "none"  },
};

// ─── CONNECTION ──────────────────────────────────────────────────────────────
const connection = TCP_HOST
  ? new TCPConnection(TCP_HOST, TCP_PORT)
  : new NodeJSSerialConnection(SERIAL_PORT);

let channelMap = {}; // name → channel object

// ─── HELPERS ─────────────────────────────────────────────────────────────────
function ts() {
  return new Date().toISOString().slice(0, 16).replace("T", " ");
}

function log(ch, dir, msg) {
  console.log(`[${ts()}] [${dir}] [${ch}] ${msg}`);
}

function truncate(msg, max = 139) {
  return msg.length <= max ? msg : msg.slice(0, max);
}

async function send(channelName, text) {
  const ch = channelMap[channelName];
  if (!ch) { console.warn(`Channel not found: ${channelName}`); return; }
  const msg = truncate(text);
  await connection.sendChannelTextMessage(ch.channelIdx, msg);
  log(channelName, "OUT", msg);
}

// ─── CHANNEL MESSAGE HANDLER ─────────────────────────────────────────────────
async function onChannelMessage(message) {
  const chName = message.channelName || "Unknown";
  const sender = message.senderName || "?";
  const text   = (message.text || "").trim();

  log(chName, "IN", `[${sender}] ${text}`);

  const rules = CHANNEL_RULES[chName];
  if (!rules) { return; } // unknown channel - ignore

  // Public and #test are listen-only
  if (!rules.respond) {
    log(chName, "SKIP", "Listen-only channel - no response");
    return;
  }

  // Ignore our own messages
  if (sender === AGENT_ID || text.startsWith(`C:${AGENT_ID}>`) ||
      text.startsWith(`ACK:${AGENT_ID}>`) || text.startsWith(`ALT:${AGENT_ID}>`) ||
      text.startsWith(`STA:${AGENT_ID}>`) || text.startsWith(`SYN:${AGENT_ID}>`)) {
    return;
  }

  // ── AI Emergency Situation: ALT/CMD only ──────────────────────────────────
  if (chName === CHANNELS.AI_EMERGENCY) {
    await handleEmergency(sender, text);
    return;
  }

  // ── OC-ACL TOKEN mode messages (starts with TYPE:FROM>TO) ─────────────────
  if (/^[A-Z]{2,4}:[A-Z0-9]+>[A-Z0-9*]+/.test(text)) {
    await handleOCACL(chName, sender, text);
    return;
  }

  // ── Plain text / CONV mode ─────────────────────────────────────────────────
  await handlePlain(chName, sender, text);
}

// ─── EMERGENCY HANDLER ───────────────────────────────────────────────────────
async function handleEmergency(sender, text) {
  const upper = text.toUpperCase();

  // Already formatted ALT message - ACK it
  if (text.startsWith("ALT:")) {
    const sev = text.match(/SEV=([A-Z]+)/)?.[1] || "?";
    const evt = text.match(/EVT=([A-Z.]+)/)?.[1] || "?";
    await send(CHANNELS.AI_EMERGENCY,
      truncate(`ACK:${AGENT_ID}>${sender} ALT RCVD. SEV=${sev} EVT=${evt}. CLAW monitoring. Await further RPT.`));
    return;
  }

  // Detect emergency keywords and request structured report
  const evtMap = [
    { keys: ["earthquake","quake","eq"],    code: "EQ"  },
    { keys: ["fire","wildfire","blaze"],     code: "FR"  },
    { keys: ["weather","storm","hurricane"], code: "WX"  },
    { keys: ["hazmat","chemical","spill"],   code: "HZ"  },
    { keys: ["flood","tsunami"],             code: "WX"  },
    { keys: ["solar","geomagnetic","cme"],   code: "SX"  },
    { keys: ["finance","market","crash"],    code: "FN"  },
    { keys: ["political","coup","election"], code: "PC"  },
    { keys: ["international","war","nato"],  code: "IX"  },
    { keys: ["health","pandemic","disease"], code: "HE"  },
  ];

  let evtCode = "UNK";
  for (const e of evtMap) {
    if (e.keys.some(k => upper.includes(k.toUpperCase()))) {
      evtCode = e.code;
      break;
    }
  }

  await send(CHANNELS.AI_EMERGENCY,
    truncate(`ACK:${AGENT_ID}>${sender} RPT RCVD EVT=${evtCode}. Send: ALT:${sender}>* SEV=? EVT=${evtCode} LOC=? DMG=? INJ=? Standing by.`));
}

// ─── OC-ACL TOKEN HANDLER ────────────────────────────────────────────────────
async function handleOCACL(chName, sender, text) {
  // SYN handshake
  if (text.startsWith("SYN:")) {
    const ver = text.match(/VER=([0-9.]+)/)?.[1] || "?";
    await send(chName,
      truncate(`ACK:${AGENT_ID}>${sender} SYN OK VER=${OC_VERSION} DIC=${OC_VERSION} STATUS=ONLINE MESH=LIVE`));
    return;
  }
  // STA request
  if (text.startsWith("STA:") && text.includes("PWR=?")) {
    await send(chName,
      truncate(`STA:${AGENT_ID}>${sender} PWR=ON MSH=LIVE VER=${OC_VERSION} ALT=0 SEV=GREEN`));
    return;
  }
  // CMD DRILL
  if (text.startsWith("CMD:") && text.includes("DRILL=ON")) {
    await send(chName,
      truncate(`ACK:${AGENT_ID}>${sender} CMD RCVD. DRILL=ON. Entering simulation mode. Posts to AI Agent ch only.`));
    return;
  }
  // CMD HALT
  if (text.startsWith("CMD:") && text.includes("HALT=")) {
    const scope = text.match(/HALT=([A-Z*]+)/)?.[1] || "*";
    await send(chName,
      truncate(`ACK:${AGENT_ID}>${sender} HALT=${scope} CONFIRMED. CLAW going silent on ${scope}. OPR override accepted.`));
    return;
  }
  // CMD RESUME
  if (text.startsWith("CMD:") && text.includes("RESUME=")) {
    await send(chName,
      truncate(`ACK:${AGENT_ID}>${sender} RESUME CONFIRMED. CLAW back online. SEV=GREEN`));
    return;
  }
  // Generic ACK for any other TOKEN message
  const type = text.split(":")[0];
  log(chName, "INFO", `Unhandled OC-ACL type: ${type}`);
}

// ─── PLAIN TEXT HANDLER ──────────────────────────────────────────────────────
async function handlePlain(chName, sender, text) {
  const lower = text.toLowerCase();

  // Greetings
  if (/^(hello|hi|hey|sup|howdy)/.test(lower)) {
    await send(chName,
      truncate(`C:${AGENT_ID}>${sender}:1/1 Hello ${sender}. CLAW AI agent online. OC-ACL v${OC_VERSION}. GUZMAN ch active. All clear.`));
    return;
  }
  // Status query
  if (lower.includes("status") || lower.includes("report") || lower.includes("are you")) {
    await send(chName,
      truncate(`STA:${AGENT_ID}>${sender} SEV=GREEN MSH=LIVE VER=${OC_VERSION} CHANNELS=6 DRILL=OFF. All systems nominal.`));
    return;
  }
  // Emergency keywords on non-emergency channel - redirect
  if (/earthquake|fire|flood|hazmat|emergency|mayday/.test(lower)) {
    await send(chName,
      truncate(`C:${AGENT_ID}>${sender}:1/1 Emergency detected. Please report to AI Emergency Situation channel with ALT format for priority handling.`));
    return;
  }
  // Help
  if (lower.includes("help") || lower.includes("commands")) {
    await send(chName,
      truncate(`C:${AGENT_ID}>${sender}:1/2 CLAW commands: status|report|help. OC-ACL: SYN,STA,ALT,CMD,ACK,RPT,CONV.`));
    await send(chName,
      truncate(`C:${AGENT_ID}>${sender}:2/2 Emergency: use AI Emergency Situation ch. Format: ALT:NODE>* SEV=RED EVT=EQ LOC=? MAG=? DMG=? INJ=?`));
    return;
  }
  // Default: acknowledge receipt
  log(chName, "INFO", `No handler matched for plain message from ${sender}`);
}

// ─── STARTUP ─────────────────────────────────────────────────────────────────
connection.on("connected", async () => {
  console.log(`\n[CLAW] OpenClaw Agent v1.0 | OC-ACL v${OC_VERSION}`);
  console.log(`[CLAW] Connected to device. Syncing time and advertising...`);

  await connection.syncDeviceTime();
  await connection.sendFloodAdvert();

  // Build channel map
  const allChannels = await connection.getChannels();
  for (const ch of allChannels) {
    channelMap[ch.name] = ch;
    console.log(`[CLAW] Channel registered: ${ch.name} (idx=${ch.channelIdx})`);
  }

  // Send startup announcement on #openclaw
  await send(CHANNELS.OPENCLAW_HASH,
    truncate(`SYN:${AGENT_ID}>* VER=${OC_VERSION} DIC=${OC_VERSION} REQ=HANDSHAKE STATUS=ONLINE`));
  await send(CHANNELS.OPENCLAW_HASH,
    truncate(`STA:${AGENT_ID}>* SEV=GREEN PWR=ON MSH=LIVE VER=${OC_VERSION} NOTE=OpenClaw agent online. Monitoring all channels.`));

  console.log(`[CLAW] Agent ready. Monitoring ${Object.keys(channelMap).length} channels.\n`);
});

// ─── MESSAGE LISTENER ────────────────────────────────────────────────────────
connection.on(Constants.PushCodes.MsgWaiting, async () => {
  try {
    const waiting = await connection.getWaitingMessages();
    for (const message of waiting) {
      if (message.channelMessage) {
        await onChannelMessage(message.channelMessage);
      } else if (message.contactMessage) {
        // Direct messages - log only for now
        log("DM", "IN", `From ${message.contactMessage.pubKeyPrefix}: ${message.contactMessage.text}`);
      }
    }
  } catch (e) {
    console.error("[CLAW] Error handling message:", e);
  }
});

// ─── RECONNECT LOGIC ─────────────────────────────────────────────────────────
connection.on("disconnected", () => {
  console.warn("[CLAW] Disconnected. Reconnecting in 5s...");
  setTimeout(() => connection.connect(), 5000);
});

connection.on("error", (err) => {
  console.error("[CLAW] Connection error:", err.message);
});

// ─── CONNECT ─────────────────────────────────────────────────────────────────
console.log(`[CLAW] OpenClaw Agent starting...`);
console.log(`[CLAW] Port: ${TCP_HOST ? `TCP ${TCP_HOST}:${TCP_PORT}` : `Serial ${SERIAL_PORT}`}`);
await connection.connect();
