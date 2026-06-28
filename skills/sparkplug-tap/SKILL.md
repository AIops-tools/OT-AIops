---
name: sparkplug-tap
description: >-
  Consume MQTT / Sparkplug B / Unified Namespace (UNS) data — bounded plain-MQTT
  reads, Sparkplug B sample (topic parsed + payload decoded), edge-node/device
  discovery from NBIRTH/DBIRTH, and live topic-tree (UNS) browse. A governed,
  MOC-gated publish/command exists but is OFF by default. Use when the task names
  MQTT, Sparkplug, UNS, a broker, or an spBv1.0 topic. Routes to the ot-aiops MCP
  server. Consume-first. For OPC-UA/Modbus/Siemens/Mitsubishi/MTConnect use the
  sibling *-tap skills; not for IT/network gear, Kubernetes, hypervisors, or backups.
---

# sparkplug-tap

MQTT / Sparkplug B / UNS consume-first telemetry via the **ot-aiops** MCP server,
using **paho-mqtt** (pure Python). Preview — validated against synthetic payloads,
NOT a live broker. Sparkplug B protobuf payloads decode when a decoder is
installed; otherwise they are reported as binary with a hint (never blocks).

## When to use
- An MQTT broker / Sparkplug B edge / UNS (`host:1883` or `:8883` TLS, `topic`).
- Sample topics, discover edge nodes, browse the namespace tree.

## When NOT to use (routing)
- OPC-UA → `opcua-tap`; Modbus → `modbus-tap`; Siemens → `s7-tap`; Mitsubishi →
  `mc-tap`; CNC → `mtconnect-tap`; cross-protocol triage → `industrial-diagnostics`.
- IT/network/Kubernetes/hypervisor/backup → not this tool.

## Read/consume tools (bounded — never an open loop)

| Tool | Params | Returns |
|------|--------|---------|
| `mqtt_read_topic` | `endpoint?, topic="", count=25, timeout_s=10` | `{messages:[{topic,payload:{encoding,json\|text\|hex_preview}}]}` |
| `sparkplug_subscribe_sample` | `endpoint?, topic="", count=25, timeout_s=10` | `{samples:[{topic, sparkplug:{group_id,message_type,edge_node_id,device_id}, payload}]}` |
| `sparkplug_node_list` | `endpoint?, timeout_s=10, count=500` | `{nodes:[{group_id,edge_node_id,born,devices[...]}]}` |
| `uns_browse` | `endpoint?, topic="#", timeout_s=10, count=500` | `{topic_count, topics[...], tree{...}}` |

Example: `sparkplug_node_list(endpoint="uns", timeout_s=15)` →
`{"node_count":2,"nodes":[{"group_id":"Plant1","edge_node_id":"Edge1","born":true,"devices":["DevA"]}]}`

## Command tool (HIGH risk · MOC · off by default)

`mqtt_publish(topic, payload, endpoint?, qos=0, retain=false, dry_run=true)`
- **OT-DANGEROUS. 未经授权勿对生产控制系统下发指令.** A command (e.g. Sparkplug
  NCMD/DCMD) can change a live system and has NO automatic inverse. Defaults to
  `dry_run=true`.
- Apply: `dry_run=false` + `OPCUA_AUDIT_APPROVED_BY`. CLI:
  `ot-aiops mqtt publish factory/cmd '{"sp":50}' --apply` (double-confirm prompt).

## Setup
`ot-aiops init` (mqtt: broker/port/topic/TLS/user) · `ot-aiops doctor` ·
`ot-aiops mcp`. Test against a local mosquitto broker. MQTT username/password is
stored encrypted; TLS optional. 缺功能提 issue/PR 欢迎留言.
