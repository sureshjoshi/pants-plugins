import logging

from experimental.nodejs.subsystem import DownloadedNpxTool, NodeJS, NpxToolRequest
from pants.core.util_rules.external_tool import (
    DownloadedExternalTool,
    ExternalToolRequest,
)
from pants.engine.platform import Platform
from pants.engine.rules import Get, collect_rules, rule
from pants.util.logging import LogLevel

logger = logging.getLogger(__name__)


@rule(level=LogLevel.DEBUG)
async def download_npx_tool(request: NpxToolRequest, node: NodeJS) -> DownloadedNpxTool:
    # Ensure nodejs is installed
    node_tool = await Get(
        DownloadedExternalTool, ExternalToolRequest, node.get_request(Platform.current)
    )

    # Get reference to npx
    plat_str = node.PLATFORM_MAPPING[Platform.current.value]
    npx_args = (
        node_tool.exe,
        f"./node-{node.version}-{plat_str}/lib/node_modules/npm/bin/npx-cli.js",
        "--yes",
        request.npm_package,
    )

    return DownloadedNpxTool(
        node_tool.digest,
        " ".join(npx_args),
        {"PATH": f"/bin:./node-{node.version}-{plat_str}/bin"},
    )


def rules():
    return (*collect_rules(),)
