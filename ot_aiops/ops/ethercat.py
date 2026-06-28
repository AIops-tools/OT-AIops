"""EtherCAT — documented preview stub (NOT implemented).

EtherCAT is a fieldbus, not a TCP request/response protocol like OPC-UA or
Modbus-TCP: reading process data requires a *master stack* that owns the bus
cycle (e.g. the ``pysoem`` Python binding around the SOEM C library, or an
IgH EtherCAT master), plus a real EtherCAT NIC and slave devices. We deliberately
do NOT bundle a heavy master dependency in this preview.

This module exists as the family's extension point: the OT protocol family is
designed to grow (OPC-UA → Modbus → EtherCAT). ``ethercat_status`` returns a
clear "not implemented in preview" message with the roadmap, rather than failing
opaquely or pretending to work.
"""

from __future__ import annotations

from typing import Any

ROADMAP_MESSAGE = (
    "EtherCAT is not implemented in this preview. Unlike OPC-UA / Modbus-TCP, "
    "EtherCAT needs a master stack that drives the bus cycle (e.g. pysoem / SOEM "
    "or an IgH master) plus a dedicated NIC and real slave devices — not bundled "
    "here to keep the install light. Roadmap: a future release may add an optional "
    "'ethercat' extra backed by pysoem for read-only PDO/SDO inspection. Want it "
    "sooner? Open a GitHub issue or PR."
)


def ethercat_status(target: Any = None) -> dict:
    """[READ][PREVIEW STUB] Report EtherCAT support status (not implemented)."""
    return {
        "protocol": "ethercat",
        "implemented": False,
        "status": "preview-stub",
        "message": ROADMAP_MESSAGE,
        "suggested_dependency": "pysoem",
    }
