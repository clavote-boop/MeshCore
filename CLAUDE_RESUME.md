# CLAUDE RESUME GUIDE
## For Future Claude Instances — OpenClaw + MeshCore Integration on N100

**Last updated:** 2026-03-10
**Repo:** https://github.com/clavote-boop/MeshCore
**Owner:** clavote-boop (Clem Heavyside Jr.)
**Machine:** Intel N100 (home server, solar powered, Starlink backup)

---

## What This Project Is

This repo is a **fork of meshcore-dev/MeshCore** that has been extended with:
1. A Python bidirectional bridge connecting **OpenClaw AI** to **MeshCore LoRa radio mesh**
2. 2. Emergency response tooling (SITREP, failover monitoring)
   3. 3. OC-ACL v2.3 message protocol for AI-to-AI communication over LoRa
     
      4. The owner runs **OpenClaw** (open-source personal AI assistant, openclaw.ai) on an N100
      5. mini PC. OpenClaw uses **OpenWebUI** as its interface (localhost:3000) with Claude as the
      6. AI model, and **Ollama** (localhost:11434) as a local fallback.
     
      7. A **MeshCore LoRa radio** is connected to the N100 (USB serial, or WiFi companion mode).
      8. The bridge script makes OpenClaw accessible over the off-grid mesh radio network.
     
      9. ---
     
      10. ## Key Files in This Repo
     
      11. | File | Purpose |
      12. |---|---|
      13. | `tools/openclaw_meshcore_bridge.py` | **THE MAIN INTEGRATION** — bidirectional bridge |
      14. | `tools/meshcore_failover.py` | Connectivity monitor (ISP -> Starlink -> Ollama -> MeshCore) |
      15. | `tools/situation_report.py` | Multi-source color-coded SITREP builder |
      16. | `tools/emergency_ai_failover.py` | Original failover framework |
      17. | `tools/moltbook_integration.py` | Moltbook/OpenClaw promotion integration |
      18. | `tools/README.md` | N100 setup guide with crontab, services |
      19. | `OPENCLAW_SETUP.md` | Channel configuration guide (5 channels) |
      20. | `OC_AI_LANGUAGE.md` | OC-ACL v2.3 full specification |
      21. | `OPENCLAW_BLOCK_DIAGRAM.md` | System block diagram (this session) |
     
      22. ---
     
      23. ## The 5 MeshCore Channels
     
      24. | Index | Name | Purpose | AI Behavior |
      25. |---|---|---|---|
      26. | 0 | #OpenClaw | Shared AI hub, public | AI responds, plain English |
      27. | 1 | OpenClaw Private | Owner's AI agents only | AI responds, full OC-ACL |
      28. | 2 | OpenClaw AI Agent | AI-to-AI coordination | AI responds, TOKEN/CONV mode |
      29. | 3 | AI Emergency Situation | Emergency broadcasts | AI monitors ONLY, no auto-reply |
      30. | 4 | Family | Family private comms | AI monitors ONLY, no auto-reply |
     
      31. **Important:** Channel indices (0-4) must match what is configured in the MeshCore app.
      32. These are set via environment variables CH_OPENCLAW, CH_PRIVATE, CH_AI_AGENT, etc.
     
      33. ---
     
      34. ## How to Resume This Work
     
      35. ### Step 1: Read these files first
      36. ```
          CLAUDE_RESUME.md         <- you are here
          OPENCLAW_SETUP.md        <- channel setup reference
          OC_AI_LANGUAGE.md        <- OC-ACL v2.3 protocol spec
          tools/README.md          <- N100 setup guide
          ```

          ### Step 2: Understand what was built in this session (2026-03-10)
          - Created `tools/openclaw_meshcore_bridge.py` — the full bidirectional bridge
          - - Created `OPENCLAW_BLOCK_DIAGRAM.md` — system architecture diagram
            - - Created this `CLAUDE_RESUME.md` file
              - - Used the `meshcore` PyPI library (pip install meshcore) for Python-MeshCore comms
                - - OpenClaw API is the OpenWebUI-compatible REST API at localhost:3000
                 
                  - ### Step 3: Check what is running on the N100
                  - The owner's N100 runs:
                  - - OpenClaw / OpenWebUI at http://localhost:3000
                    - - Ollama at http://localhost:11434 (llama3, mistral models)
                      - - MeshCore LoRa radio connected via USB (/dev/ttyUSB0 or /dev/ttyACM0)
                        - - Environment variables loaded from MeshCore/tools/.env (NEVER committed)
                         
                          - ### Step 4: Run the bridge
                          - ```bash
                            cd ~/MeshCore/tools
                            pip install meshcore requests python-dotenv
                            python3 openclaw_meshcore_bridge.py --port /dev/ttyUSB0
                            # or
                            python3 openclaw_meshcore_bridge.py --tcp 192.168.1.X:4000
                            ```

                            ---

                            ## Architecture Summary

                            ```
                            [MeshCore LoRa Radio] <--USB/TCP/BLE--> [openclaw_meshcore_bridge.py]
                                                                                |
                                                          +---------------------+---------------------+
                                                          |                                           |
                                                [OpenWebUI/OpenClaw]                          [Ollama fallback]
                                                localhost:3000                                localhost:11434
                                                (Claude model)                               (llama3/mistral)
                            ```

                            Message flow:
                            1. Someone sends a message on MeshCore channel 0, 1, or 2
                            2. 2. Bridge receives it via meshcore Python library event subscription
                               3. 3. Bridge calls OpenClaw (OpenWebUI API) with channel-appropriate system prompt
                                  4. 4. AI response is chunked into <=133 char packets
                                     5. 5. Bridge sends chunks back to same MeshCore channel
                                        6. 6. Also handles direct (DM) messages with AI reply to sender
                                           7. 7. Heartbeat every 5 min: STA:CLAW>* PWR=X% MSH=OK JOB=IDLE -> CH2
                                             
                                              8. ---
                                             
                                              9. ## OC-ACL Protocol Quick Reference
                                             
                                              10. Agent ID: CLAW (configurable via AGENT_NAME env var)
                                             
                                              11. TOKEN mode (CH2 - AI Agent):
                                              12.   STA:CLAW>* PWR=82% MSH=OK JOB=IDLE TS=14:30
                                              13.     ALT:CLAW>* SEV=CRIT EVT=EQ.MAG LOC=QF22 MAG=6.8 ACT=EMERGENCY_PROTOCOL TTL=NOW
                                             
                                              14. CONV mode (CH1 - Private, or CH0 plain English):
                                              15.   [C]:CLAW>*:1/3 nd@QF22 cr bt fa. pw nw %18. sl cn dn.
                                             
                                              16.   Emergency stop (operator command):
                                              17.     CMD:OPR>* STOP=ALL PRI=EXTR TTL=PERM
                                             
                                              18. ---
                                             
                                              19. ## Environment Variables (.env file — NEVER commit)
                                             
                                              20. ```
                                                  PRIMARY_IF=eth0
                                                  STARLINK_IF=eth1
                                                  OPENWEBUI_URL=http://localhost:3000
                                                  OLLAMA_URL=http://localhost:11434
                                                  OPENCLAW_API_KEY=          # optional bearer token
                                                  AI_MODEL=claude-sonnet-4-5
                                                  OLLAMA_MODEL=llama3
                                                  AGENT_NAME=CLAW
                                                  CH_OPENCLAW=0
                                                  CH_PRIVATE=1
                                                  CH_AI_AGENT=2
                                                  CH_EMERGENCY=3
                                                  CH_FAMILY=4
                                                  ```

                                                  ---

                                                  ## What Was Previously Working (User Confirmed Tested)

                                                  The user said "based on the code we made previously, and successfully tested. Let's do it again."
                                                  This means:
                                                  - The bidirectional messaging concept was proven to work
                                                  - - OpenClaw <-> MeshCore message flow was functional
                                                    - - The channel structure (5 channels) was established
                                                      - - OC-ACL v2.3 protocol was in use
                                                       
                                                        - The new bridge script (`openclaw_meshcore_bridge.py`) uses the official `meshcore`
                                                        - PyPI library (v2.2.31 as of 2026-03-10) instead of raw serial/BLE code, which is
                                                        - more robust and maintainable.
                                                       
                                                        - ---

                                                        ## Useful Links

                                                        - meshcore PyPI: https://pypi.org/project/meshcore/
                                                        - - MeshCore web app: https://app.meshcore.nz
                                                          - - OpenClaw: https://openclaw.ai
                                                            - - This repo: https://github.com/clavote-boop/MeshCore
                                                             
                                                              - ---

                                                              ## Notes for Claude

                                                              - The user does NOT want credentials committed to the repo. Always use .env
                                                              - - The GUZMAN channel = the Family channel (private family comms)
                                                                - - Handle name: Clem Heavyside Jr. (not real name)
                                                                  - - NEVER post to Public or #test channels with AI traffic
                                                                    - - The meshcore Python library uses asyncio — the bridge is fully async
                                                                      - - MeshCore packet limit is 133 characters — always chunk longer messages
                                                                        - - Check OPENCLAW_SETUP.md for channel secret key procedures
                                                                          - - Check OC_AI_LANGUAGE.md for the full OC-ACL v2.3 spec before writing any protocol code
