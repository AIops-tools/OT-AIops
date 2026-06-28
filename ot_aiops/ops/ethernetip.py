"""EtherNet/IP (Rockwell / Allen-Bradley) — documented preview stub (NOT implemented).

EtherNet/IP (CIP over TCP/UDP) is the dominant Rockwell/Allen-Bradley protocol
(ControlLogix / CompactLogix / Micro800). Reading tags requires a CIP client that
speaks the Logix tag/UDT model; the planned library is ``pycomm3`` (pure Python,
read/write Logix tags). We deliberately do NOT add that dependency in this
preview to keep the install light and avoid implying live-PLC validation.

This module is the family's Rockwell extension point, mirroring the EtherCAT
stub: ``ethernetip_status`` returns a clear "not implemented in preview" message
with the roadmap, rather than failing opaquely or pretending to work.
"""

from __future__ import annotations

from typing import Any

ROADMAP_MESSAGE = (
    "EtherNet/IP (Rockwell / Allen-Bradley, CIP) is not implemented in this "
    "preview. Reading Logix tags needs a CIP client that models the Logix "
    "tag/UDT space — planned library: 'pycomm3' (pure Python, ControlLogix / "
    "CompactLogix / Micro800). Deliberately not bundled yet to keep the install "
    "light and avoid implying live-PLC validation. Roadmap: a future release may "
    "add an optional 'enip' extra backed by pycomm3 for read-first Logix tag "
    "access. Want it sooner? Open a GitHub issue or PR."
)


def ethernetip_status(target: Any = None) -> dict:
    """[READ][PREVIEW STUB] Report EtherNet/IP support status (not implemented)."""
    return {
        "protocol": "ethernetip",
        "implemented": False,
        "status": "preview-stub",
        "message": ROADMAP_MESSAGE,
        "suggested_dependency": "pycomm3",
    }
