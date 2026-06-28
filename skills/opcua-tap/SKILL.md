---
name: opcua-tap
description: >-
  Read OPC-UA servers (opc.tcp) — browse the node tree, read node values with
  datatype/timestamp/status, bounded sampling, server info, best-effort
  alarm/condition surfacing, and threshold/anomaly health. Use when the task
  names OPC-UA, an opc.tcp:// endpoint, or a SCADA/PLC gateway exposing OPC-UA.
  Routes to the ot-aiops MCP server. Read-only. Do NOT use for IT/network gear,
  Kubernetes, hypervisors, or backups; for Modbus/S7/Mitsubishi/MTConnect/MQTT
  use the sibling *-tap skills.
---

# opcua-tap

Read-only OPC-UA telemetry + problem surfacing via the **ot-aiops** MCP server.
Preview — validated against an in-process asyncua simulator, NOT live SCADA.

## When to use
- An OPC-UA server / PLC gateway (`opc.tcp://host:4840`), anonymous or user/pass.
- Discover the address space, read tags, sample a node, surface alarms.

## When NOT to use (routing)
- Modbus → `modbus-tap`; Siemens S7 → `s7-tap`; Mitsubishi → `mc-tap`; CNC
  machine tools → `mtconnect-tap`; MQTT/Sparkplug/UNS → `sparkplug-tap`.
- Cross-protocol "why no data" / alarm-flood / tag-health → `industrial-diagnostics`.
- IT/network devices, Kubernetes, hypervisors, backups → not this tool.

## Tools

| Tool | Params | Returns |
|------|--------|---------|
| `opcua_server_info` | `endpoint?` | `{state, product_name, namespaces[...]}` |
| `opcua_browse` | `node_id="i=85", endpoint?, depth=2` | `[{node_id, browse_name, node_class, depth, parent}]` |
| `opcua_read_node` | `node_id, endpoint?` | `{value, datatype, source_timestamp, status_code, good}` |
| `opcua_read_many` | `node_ids[], endpoint?` | `[{node_id, value, ...}]` |
| `opcua_subscribe_sample` | `node_id, endpoint?, samples=5, interval_ms=500, timeout_s=30` | `{collected, samples[...]}` (bounded) |
| `opcua_read_alarms` | `endpoint?, node_id="i=85", depth=4` | `{active_alarms[...], active_count}` |
| `health_summary` | `endpoint?, node_ids[]?, thresholds?` | `{overall, counts, offenders[...]}` |
| `anomaly_scan` | `node_id, endpoint?, samples=20, interval_ms=200, sigma=3.0` | `{mean, stddev, outliers[...]}` |

## Example
`opcua_read_node(node_id="ns=2;i=5", endpoint="line1")`
→ `{"value":85.0,"datatype":"Double","source_timestamp":"2026-06-28T10:00:00Z","good":true}`

## Setup
`ot-aiops init` (add an opcua endpoint) · `ot-aiops doctor` · `ot-aiops mcp`.
Config: `~/.ot-aiops/config.yaml`; secrets encrypted in `secrets.enc`, unlocked
via `OT_AIOPS_MASTER_PASSWORD`.

## Safety
Read-only. Cert/message security (Sign/Encrypt) is roadmap — only anonymous +
user/pass are validated. Endpoint text is sanitized; secrets are never returned.
Missing a feature? 缺功能提 issue/PR 欢迎留言.
