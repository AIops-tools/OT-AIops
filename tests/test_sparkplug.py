"""MQTT / Sparkplug B ops tests with synthetic payloads (no live broker).

The bounded collector ``_collect`` is monkeypatched to return synthetic messages,
so payload decoding, Sparkplug topic parsing, node discovery, UNS browse, and the
publish dry-run gate are all exercised without a broker.
"""

from __future__ import annotations

import pytest

from ot_aiops.config import TargetConfig
from ot_aiops.ops import sparkplug_ops as ops

TARGET = TargetConfig(name="uns", protocol="mqtt", host="broker", topic="spBv1.0/#")


@pytest.mark.unit
def test_decode_json_payload():
    out = ops._decode_payload(b'{"temp": 21.5}')
    assert out["encoding"] == "json"
    assert out["json"]["temp"] == 21.5


@pytest.mark.unit
def test_decode_text_payload():
    out = ops._decode_payload(b"AVAILABLE")
    assert out["encoding"] == "text"
    assert out["text"] == "AVAILABLE"


@pytest.mark.unit
def test_decode_binary_payload_is_not_fatal():
    out = ops._decode_payload(b"\x08\x96\x01\x12\x07metric")
    assert out["encoding"] in ("binary", "sparkplug_b")
    if out["encoding"] == "binary":
        assert "hex_preview" in out and "note" in out


@pytest.mark.unit
def test_parse_sparkplug_topic():
    p = ops._parse_sparkplug_topic("spBv1.0/Plant1/NBIRTH/EdgeNode5/Dev2")
    assert p["group_id"] == "Plant1"
    assert p["message_type"] == "NBIRTH"
    assert p["edge_node_id"] == "EdgeNode5"
    assert p["device_id"] == "Dev2"
    assert ops._parse_sparkplug_topic("factory/line1/temp") is None


def _fake_messages():
    return [
        {"topic": "spBv1.0/Plant1/NBIRTH/Edge1", "payload": b'{"online": true}'},
        {"topic": "spBv1.0/Plant1/DBIRTH/Edge1/DevA", "payload": b'{"x": 1}'},
        {"topic": "spBv1.0/Plant1/DDATA/Edge1/DevA", "payload": b'{"x": 2}'},
        {"topic": "spBv1.0/Plant2/NBIRTH/Edge9", "payload": b'{"online": true}'},
    ]


@pytest.fixture
def patched_collect(monkeypatch):
    monkeypatch.setattr(ops, "_collect", lambda t, topic, count, timeout_s: _fake_messages())


@pytest.mark.unit
def test_sparkplug_node_list(patched_collect):
    out = ops.sparkplug_node_list(TARGET)
    keys = {(n["group_id"], n["edge_node_id"]) for n in out["nodes"]}
    assert ("Plant1", "Edge1") in keys
    assert ("Plant2", "Edge9") in keys
    plant1 = next(n for n in out["nodes"] if n["edge_node_id"] == "Edge1")
    assert plant1["born"] is True
    assert "DevA" in plant1["devices"]


@pytest.mark.unit
def test_uns_browse_builds_tree(patched_collect):
    out = ops.uns_browse(TARGET, topic="spBv1.0/#")
    assert out["topic_count"] == 4
    assert "spBv1.0" in out["tree"]
    assert "Plant1" in out["tree"]["spBv1.0"]


@pytest.mark.unit
def test_mqtt_read_topic_decodes(patched_collect):
    out = ops.mqtt_read_topic(TARGET, topic="spBv1.0/#")
    assert out["message_count"] == 4
    assert out["messages"][0]["payload"]["encoding"] == "json"


@pytest.mark.unit
def test_sparkplug_subscribe_sample_parses_topic(patched_collect):
    out = ops.sparkplug_subscribe_sample(TARGET)
    assert out["samples"][1]["sparkplug"]["message_type"] == "DBIRTH"


@pytest.mark.unit
def test_mqtt_publish_dry_run_does_not_publish():
    out = ops.mqtt_publish(TARGET, "factory/cmd", '{"setpoint": 50}', dry_run=True)
    assert out["dry_run"] is True
    assert out["would_publish_bytes"] > 0
    assert "未经授权" in out["note"]
