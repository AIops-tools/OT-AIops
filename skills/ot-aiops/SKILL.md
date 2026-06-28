---
name: ot-aiops
description: >-
  Vendor-neutral, governed industrial/OT data tap + intelligent troubleshooting.
  Read (and, gated, write) PLCs, controllers, machine tools and IIoT brokers over
  OPC-UA, Modbus-TCP, Siemens S7comm, Mitsubishi MC, MTConnect, MQTT/Sparkplug B,
  and Allen-Bradley EtherNet/IP — plus cross-protocol diagnostics ("no-data"
  dataflow diagnosis, ISA-18.2 alarm bad-actors, tag/historian health) and
  analytics (OEE/downtime, asset inventory, OPC-UA HDA, change-of-value). Use when
  the task names any industrial protocol, a PLC/SCADA/HMI/historian/CNC, an
  opc.tcp:// or mqtt:// endpoint, OEE/downtime, or OT asset inventory. Routes to
  the ot-aiops MCP server. Read-first; writes are MOC-gated (high risk, dry-run +
  double-confirm). Do NOT use for IT/network gear, Kubernetes, hypervisors, or
  backups — those are separate AIops tools.
---

# ot-aiops — industrial data tap + intelligent troubleshooting

One governed MCP server exposing **51 tools** across 7 industrial protocols plus a
cross-protocol intelligence layer. Every tool runs through the ot-aiops governance
harness (audit / budget / risk-tier / undo). **Read-first.** The 4 write tools are
gated as Management-of-Change: `risk=HIGH`, `dry_run=True` by default, CLI requires
a double-confirm, the before-value is captured for undo. **Never write to a
production control system without authorization.** Preview / mock-or-sim validated —
verify against live equipment. Start with `protocols_supported` to see what's
configured and `<protocol> doctor` to test a link.

## When to route here
Task mentions: OPC-UA / opc.tcp, Modbus, Siemens S7 / S7-1200/1500, Mitsubishi /
MELSEC, MTConnect / CNC machine monitoring, MQTT / Sparkplug B / Unified Namespace,
Allen-Bradley / ControlLogix / CompactLogix / EtherNet-IP, OEE / downtime, OT asset
inventory, "no data / stale tag" diagnosis, alarm flood / ISA-18.2.

## Tools by protocol

### OPC-UA (read-only) — opc.tcp endpoints
- `opcua_server_info` — status, build info, namespace array
- `opcua_browse` — browse node tree from a node id (bounded depth)
- `opcua_read_node` — value + datatype + source timestamp + status code
- `opcua_read_many` — batch read node ids (bounded)
- `opcua_subscribe_sample` — bounded sampling, then returns (never loops)
- `opcua_read_alarms` — best-effort active alarm/condition surfacing
- `opcua_read_history` — Historical Access (HDA): raw history over a [start,end] window
- `health_summary` — classify node-ids vs warn/alarm thresholds
- `anomaly_scan` — sample a node, flag statistical outliers

### Modbus-TCP (read-only here)
- `modbus_read_holding` (FC03), `modbus_read_input` (FC04), `modbus_read_coils`
  (FC01), `modbus_read_discrete` (FC02) — with decode hints
- `modbus_health_summary` — classify registers vs thresholds

### Siemens S7comm (pyS7; S7-300/400/1200/1500)
- `s7_cpu_info` — CPU identity + run/stop
- `s7_read_area` — read N items of a type from an S7 memory area
- `s7_read_db` — read N items from a data block
- `s7_read_many` — batch raw pyS7 address strings
- `s7_write_db` — **[WRITE][HIGH][MOC]** write one value to a DB (off by default)

### Mitsubishi MC (pymcprotocol 3E; Q/L/iQ)
- `mc_cpu_status` — MELSEC CPU type/code
- `mc_read_words` / `mc_read_bits` — batch word/bit devices from a head device
- `mc_read_many` — random-read scattered word + dword in one request
- `mc_write_words` — **[WRITE][HIGH][MOC]** write words (off by default)

### MTConnect (read-only; all CNC machine tools)
- `mtconnect_probe` — device model (devices → components → data items)
- `mtconnect_current` — latest value of every data item (machine snapshot)
- `mtconnect_sample` — bounded stream of recent observations
- `mtconnect_assets` — cutting tools / fixtures / programs
- `mtconnect_oee_snapshot` — availability / execution / mode / program (OEE inputs)

### MQTT / Sparkplug B / UNS (paho-mqtt; full Tahu protobuf decode)
- `mqtt_read_topic` — plain MQTT bounded message collect
- `sparkplug_decode_payload` — decode one raw Sparkplug B payload to metrics
- `sparkplug_subscribe_sample` — bounded sample w/ full decode + birth/death/seq
- `sparkplug_node_list` — edge nodes/devices + online state + primary-host STATE
- `uns_browse` — browse the live topic tree (UNS) under a filter (bounded)
- `mqtt_publish` — **[WRITE][HIGH][MOC]** publish/command to a topic (off by default)

### Allen-Bradley EtherNet/IP (pycomm3; ControlLogix/CompactLogix)
- `eip_controller_info` — controller identity (proves the CIP link)
- `eip_list_tags` — discover controller tag list (names/types/structures)
- `eip_read_tag` — read one tag (or array element) with its type
- `eip_read_many` — batch read (auto multi-packet)
- `eip_write_tag` — **[WRITE][HIGH][MOC]** write one tag value (off by default)

## Cross-protocol intelligence

### Diagnostics — `skills` umbrella: troubleshooting
- `diagnose_dataflow` — localize a "no data" break across an endpoint's reachable hops
- `historian_health` — bad-tag / flatline / gap detection over a series
- `alarm_bad_actors` — ISA-18.2 alarm-flood analysis (rate vs <6/12/30, Pareto
  offenders, chattering, standing) over an event list
- `tag_health` — rank tag offenders by bad-quality / flatline / range / anomaly

### Analytics
- `oee_compute` — OEE = Availability × Performance × Quality
- `downtime_events` — detect running→stopped transitions, categorize stoppages
- `oee_multidim` — aggregate OEE across machine × part × shift
- `asset_inventory` — actively fingerprint endpoints (vendor/model/firmware/protocol)
  into an asset register (active discovery, **not** passive SPAN/tap)
- `monitor_changes` — capture only the value CHANGES of a point over a bounded window

### Meta / roadmap
- `protocols_supported` — capability map (protocols, status, tools, connection params)
- `ethercat_status` — preview stub (EtherCAT not implemented yet)
- EtherNet/IP roadmap: PLC-5 / SLC (PCCC), Micro800; passive asset discovery; OPC-UA
  certificate security.

## Setup
`ot-aiops init` (interactive wizard, per-protocol prompts) writes
`~/.ot-aiops/config.yaml`; credentials go to the encrypted store
(`~/.ot-aiops/secrets.enc`, master password via `OT_AIOPS_MASTER_PASSWORD`). Run
`ot-aiops doctor` to probe each configured endpoint. Full per-protocol reference,
connection params, simulator-test guide, and MCP JSON examples are in the README.

## Safety
Read-first. The 4 write tools (`s7_write_db`, `mc_write_words`, `mqtt_publish`,
`eip_write_tag`) default to `dry_run=True`, require a CLI double-confirm, and record
an undo descriptor from the captured before-value. Do not point this at production
control systems without authorization. No tool returns secrets.
