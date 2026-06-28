"""MCP server wrapping ot-aiops operations (stdio transport).

Thin adapter layer: each ``@mcp.tool()`` function (in ``mcp_server/tools/``)
delegates to the ``ot_aiops`` ops package and is wrapped with the ot-aiops
``@governed_tool`` harness (audit / budget / risk-tier).

Standalone, self-governed, vendor-neutral OT data tap + intelligent
troubleshooting (preview) over OPC-UA, Modbus-TCP, S7comm, Mitsubishi MC,
MTConnect, and MQTT/Sparkplug B, plus EtherNet/IP and EtherCAT roadmap stubs.
Read-first; the few write/command tools are MOC-gated (high risk_tier).

Source: https://github.com/AIops-tools/OT-AIops
License: MIT
"""

import logging

from mcp_server._shared import _safe_error, mcp, tool_errors

# Importing the tool modules registers every @mcp.tool() onto the shared
# `mcp` instance. Order does not matter; each module is self-contained.
from mcp_server.tools import (  # noqa: F401 — side effects
    analysis_tools,
    diagnostics_tools,
    ethercat_tools,
    ethernetip_tools,
    mc_tools,
    modbus_tools,
    mtconnect_tools,
    opcua_tools,
    overview_tools,
    s7_tools,
    sparkplug_tools,
)

__all__ = ["mcp", "main", "_safe_error", "tool_errors"]


def main() -> None:
    """Run the MCP server over stdio."""
    logging.basicConfig(level=logging.INFO)
    mcp.run(transport="stdio")
