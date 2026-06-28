"""EtherCAT MCP tool — documented preview stub (not implemented)."""

from typing import Optional

from mcp_server._shared import mcp, tool_errors
from ot_aiops.governance import governed_tool
from ot_aiops.ops import ethercat


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors("dict")
def ethercat_status(endpoint: Optional[str] = None) -> dict:
    """[READ][PREVIEW STUB] EtherCAT support status — not implemented yet.

    Returns a clear roadmap message: EtherCAT needs a master stack (e.g. pysoem)
    plus a dedicated NIC and slave devices, deliberately not bundled in this
    preview. The OT family's extension point for a future release.

    Args:
        endpoint: Endpoint name (unused; accepted for interface symmetry).
    """
    return ethercat.ethercat_status(endpoint)
