"""MQTT / Sparkplug B / UNS operations (consume-first).

The Unified Namespace (UNS) and Sparkplug B sit on top of MQTT (``paho-mqtt``,
pure Python). This module is **consume/read primary**: it subscribes to a broker,
collects a BOUNDED number of messages (never an open-ended loop), and returns
them — decoded as JSON/text where possible. Sparkplug B uses a protobuf payload;
if no protobuf decoder is installed the payload is reported as binary (with a
hex preview and a clear hint) rather than blocking — so a live broker is never
required to import or test this module.

Topic parsing follows the Sparkplug B convention
``spBv1.0/{group}/{msg_type}/{edge_node}/[device]`` (msg_type ∈ NBIRTH, DBIRTH,
NDATA, DDATA, …); node discovery reads NBIRTH/DBIRTH.

``mqtt_publish`` is an OT-DANGEROUS command path: governed (high risk_tier),
off by default (dry-run), and carries an explicit safety note. A published
command has no automatic inverse. 未经授权勿对生产控制系统下发指令.
"""

from __future__ import annotations

import json
import time
from typing import Any

from ot_aiops.connection import OTConnectionError, mqtt_session
from ot_aiops.ops._shared import s

MAX_MESSAGES = 500
DEFAULT_MESSAGES = 25
DEFAULT_TIMEOUT_S = 10
MAX_TIMEOUT_S = 60
_POLL_S = 0.05


def _clamp_count(count: int) -> int:
    return max(1, min(int(count), MAX_MESSAGES))


def _clamp_timeout(timeout_s: int) -> int:
    return max(1, min(int(timeout_s), MAX_TIMEOUT_S))


def _collect(target: Any, topic: str, count: int, timeout_s: int) -> list[dict]:
    """Subscribe to ``topic`` and collect up to ``count`` messages (bounded).

    Factored out (and monkeypatched in tests) so the parsing/decoding tools can
    be exercised with synthetic messages and no live broker.
    """
    topic = topic or getattr(target, "topic", "") or "#"
    count = _clamp_count(count)
    timeout_s = _clamp_timeout(timeout_s)
    buffer: list[dict] = []

    def _on_message(_client: Any, _userdata: Any, msg: Any) -> None:
        if len(buffer) < count:
            buffer.append({"topic": msg.topic, "payload": bytes(msg.payload)})

    with mqtt_session(target) as client:
        client.on_message = _on_message
        client.subscribe(topic)
        deadline = time.monotonic() + timeout_s
        while len(buffer) < count and time.monotonic() < deadline:
            time.sleep(_POLL_S)
    return buffer


def _decode_payload(payload: bytes) -> dict:
    """Best-effort decode of an MQTT payload to a JSON-safe descriptor."""
    if not payload:
        return {"encoding": "empty"}
    text: str | None = None
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError:
        text = None
    if text is not None:
        stripped = text.strip()
        if stripped[:1] in ("{", "["):
            try:
                return {"encoding": "json", "json": json.loads(stripped)}
            except json.JSONDecodeError:
                pass
        if text.isprintable():
            return {"encoding": "text", "text": s(text, 512)}
    metrics = _try_sparkplug_protobuf(payload)
    if metrics is not None:
        return {"encoding": "sparkplug_b", "metrics": metrics}
    return {
        "encoding": "binary",
        "bytes": len(payload),
        "hex_preview": payload[:32].hex(),
        "note": "Binary payload (likely Sparkplug B protobuf). Install a Sparkplug "
        "decoder ('tahu') or publish JSON/UNS payloads to see values.",
    }


def _try_sparkplug_protobuf(payload: bytes) -> list[dict] | None:
    """Decode a Sparkplug B protobuf payload if a decoder is available, else None."""
    try:  # pragma: no cover — only runs when an optional decoder is installed
        from tahu import sparkplug_b_pb2  # type: ignore[import-not-found]
    except ImportError:
        return None
    try:  # pragma: no cover
        pb = sparkplug_b_pb2.Payload()
        pb.ParseFromString(payload)
        return [
            {"name": s(m.name, 96), "value": s(str(getattr(m, m.WhichOneof("value"), "")), 128)}
            for m in pb.metrics
        ][:MAX_MESSAGES]
    except Exception:  # noqa: BLE001 — malformed payload is not our crash
        return None


def _parse_sparkplug_topic(topic: str) -> dict | None:
    """Parse a Sparkplug B topic into its components, or None if not Sparkplug."""
    parts = topic.split("/")
    if len(parts) >= 4 and parts[0].lower().startswith("spbv"):
        return {
            "namespace": s(parts[0], 16),
            "group_id": s(parts[1], 64),
            "message_type": s(parts[2], 16),
            "edge_node_id": s(parts[3], 96),
            "device_id": s(parts[4], 96) if len(parts) > 4 else "",
        }
    return None


def mqtt_read_topic(
    target: Any, topic: str = "", count: int = DEFAULT_MESSAGES, timeout_s: int = DEFAULT_TIMEOUT_S
) -> dict:
    """[READ] Plain MQTT: collect a BOUNDED set of messages from a topic filter."""
    msgs = _collect(target, topic, count, timeout_s)
    return {
        "endpoint": s(target.name, 64),
        "topic": s(topic or getattr(target, "topic", "") or "#", 128),
        "message_count": len(msgs),
        "messages": [
            {"topic": s(m["topic"], 128), "payload": _decode_payload(m["payload"])}
            for m in msgs
        ],
    }


def sparkplug_subscribe_sample(
    target: Any, topic: str = "", count: int = DEFAULT_MESSAGES, timeout_s: int = DEFAULT_TIMEOUT_S
) -> dict:
    """[READ] Bounded Sparkplug B sample: topic parsed + payload decoded."""
    topic = topic or getattr(target, "topic", "") or "spBv1.0/#"
    msgs = _collect(target, topic, count, timeout_s)
    samples = []
    for m in msgs:
        samples.append(
            {
                "topic": s(m["topic"], 128),
                "sparkplug": _parse_sparkplug_topic(m["topic"]),
                "payload": _decode_payload(m["payload"]),
            }
        )
    return {
        "endpoint": s(target.name, 64),
        "topic": s(topic, 128),
        "message_count": len(samples),
        "samples": samples,
    }


def sparkplug_node_list(
    target: Any, timeout_s: int = DEFAULT_TIMEOUT_S, count: int = MAX_MESSAGES
) -> dict:
    """[READ] Discover edge nodes / devices from NBIRTH / DBIRTH announcements."""
    msgs = _collect(target, "spBv1.0/#", count, timeout_s)
    nodes: dict[str, dict] = {}
    for m in msgs:
        parsed = _parse_sparkplug_topic(m["topic"])
        if not parsed:
            continue
        mtype = parsed["message_type"].upper()
        key = f"{parsed['group_id']}/{parsed['edge_node_id']}"
        node = nodes.setdefault(
            key,
            {
                "group_id": parsed["group_id"],
                "edge_node_id": parsed["edge_node_id"],
                "devices": set(),
                "born": False,
            },
        )
        if mtype in ("NBIRTH",):
            node["born"] = True
        if parsed["device_id"]:
            node["devices"].add(parsed["device_id"])
    discovered = [
        {
            "group_id": n["group_id"],
            "edge_node_id": n["edge_node_id"],
            "born": n["born"],
            "devices": sorted(n["devices"]),
        }
        for n in nodes.values()
    ]
    return {
        "endpoint": s(target.name, 64),
        "node_count": len(discovered),
        "nodes": discovered,
        "note": "Discovered from observed BIRTH/DATA topics within the time window. "
        "Re-run with a longer timeout_s if nodes publish infrequently.",
    }


def uns_browse(
    target: Any, topic: str = "#", timeout_s: int = DEFAULT_TIMEOUT_S, count: int = MAX_MESSAGES
) -> dict:
    """[READ] Browse the live topic tree (UNS) under a topic filter (bounded)."""
    msgs = _collect(target, topic, count, timeout_s)
    tree: dict[str, Any] = {}
    topics: set[str] = set()
    for m in msgs:
        topics.add(m["topic"])
        node = tree
        for seg in m["topic"].split("/")[:12]:
            node = node.setdefault(s(seg, 64), {})
    return {
        "endpoint": s(target.name, 64),
        "filter": s(topic, 128),
        "topic_count": len(topics),
        "topics": sorted(s(t, 128) for t in topics)[:MAX_MESSAGES],
        "tree": tree,
    }


def mqtt_publish(
    target: Any,
    topic: str,
    payload: str,
    *,
    qos: int = 0,
    retain: bool = False,
    dry_run: bool = True,
) -> dict:
    """[WRITE][HIGH RISK] Publish/command to an MQTT topic (off by default).

    OT-dangerous: an MQTT command (e.g. a Sparkplug NCMD/DCMD) can change a live
    control system and has no automatic inverse. Refuses to act unless
    ``dry_run`` is explicitly False. 未经授权勿对生产控制系统下发指令.
    """
    qos = max(0, min(int(qos), 2))
    if dry_run:
        return {
            "endpoint": s(target.name, 64),
            "topic": s(topic, 128),
            "dry_run": True,
            "would_publish_bytes": len(payload.encode("utf-8")),
            "qos": qos,
            "retain": bool(retain),
            "note": "Dry run — nothing published. Re-run with dry_run=False AND a "
            "recorded approver to send. A published command cannot be auto-undone. "
            "未经授权勿对生产控制系统下发指令.",
        }
    with mqtt_session(target) as client:
        info = client.publish(topic, payload=payload, qos=qos, retain=bool(retain))
        try:
            info.wait_for_publish(timeout=DEFAULT_TIMEOUT_S)
        except Exception:  # noqa: BLE001 — best-effort confirmation
            pass
    return {
        "endpoint": s(target.name, 64),
        "topic": s(topic, 128),
        "dry_run": False,
        "published_bytes": len(payload.encode("utf-8")),
        "qos": qos,
        "retain": bool(retain),
        "applied": True,
    }


__all__ = [
    "mqtt_read_topic",
    "sparkplug_subscribe_sample",
    "sparkplug_node_list",
    "uns_browse",
    "mqtt_publish",
    "OTConnectionError",
]
