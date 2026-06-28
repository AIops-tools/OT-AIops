"""EtherNet/IP MCP tool — Rockwell/Allen-Bradley roadmap stub (not implemented)."""

from typing import Optional

from mcp_server._shared import mcp, tool_errors
from ot_aiops.governance import governed_tool
from ot_aiops.ops import ethernetip


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors("dict")
def ethernetip_status(endpoint: Optional[str] = None) -> dict:
    """[READ][PREVIEW STUB] EtherNet/IP (Rockwell/AB) support status — not implemented.

    Returns a clear roadmap message: reading Logix tags needs a CIP client
    (planned library: pycomm3, pure Python), deliberately not bundled in this
    preview. The family's Rockwell extension point.

    Args:
        endpoint: Endpoint name (unused; accepted for interface symmetry).

    Returns dict: {protocol, implemented:false, status:'preview-stub', message,
        suggested_dependency:'pycomm3'}.
    """
    return ethernetip.ethernetip_status(endpoint)
