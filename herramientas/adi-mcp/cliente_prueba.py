"""Smoke test: launch `adi-mcp` over stdio with the official SDK and send tools/list.

Usage:  python cliente_prueba.py            (uses `adi-mcp` from PATH)
        python cliente_prueba.py python -m adi_mcp.server
"""
from __future__ import annotations

import asyncio
import json
import sys

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


def _attr(obj, *names):
    """First existing attribute (mcp 2.x uses snake_case, 1.x camelCase)."""
    for n in names:
        if hasattr(obj, n):
            return getattr(obj, n)
    return None


async def run(command: str, args: list[str]) -> None:
    params = StdioServerParameters(command=command, args=args)
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            init = await session.initialize()
            info = _attr(init, "server_info", "serverInfo")
            print(f"server: {info.name} {info.version}  protocol {_attr(init, 'protocol_version', 'protocolVersion')}")
            tools = await session.list_tools()
            print("tools/list:")
            for t in tools.tools:
                schema = _attr(t, "input_schema", "inputSchema") or {}
                print(f"  - {t.name}({', '.join(schema.get('properties', {}))})")
            res = await session.call_tool("lookup_occupation", {"isco_or_title": "2631"})
            payload = _attr(res, "structured_content", "structuredContent") or json.loads(res.content[0].text)
            print("tools/call lookup_occupation('2631'):")
            print(json.dumps(payload, ensure_ascii=False, indent=2)[:1200])


if __name__ == "__main__":
    argv = sys.argv[1:] or ["adi-mcp"]
    asyncio.run(run(argv[0], argv[1:]))
