# adi-mcp

MCP server (stdio) for the **Agent Delegability Index (ADI)** so that Claude Code, Claude
Desktop and other MCP clients can query and cite the index. Built on the official `mcp` Python
SDK (`MCPServer`/FastMCP); data is bundled via `adi-index`, no network access.

## Install

```bash
pip install adi-mcp          # pulls adi-index
# from the repo: pip install -e herramientas/adi-index -e herramientas/adi-mcp
```

## Register

Claude Code:

```bash
claude mcp add adi -- adi-mcp
```

Claude Desktop (`claude_desktop_config.json`) or any client that takes the standard JSON:

```json
{
  "mcpServers": {
    "adi": {
      "command": "adi-mcp",
      "args": []
    }
  }
}
```

If `adi-mcp` is not on PATH, use the interpreter: `"command": "/path/to/.venv/bin/python",
"args": ["-m", "adi_mcp.server"]`.

## Tools

| Tool | Arguments | Returns |
|---|---|---|
| `lookup_occupation` | `isco_or_title` (4-digit ISCO-08 code or title substring) | `match` (full ADI record), `candidates` when searching by title |
| `country_profile` | `iso3` | `profile` from the atlas |
| `top_occupations` | `n` (default 10), `level` `l2`/`l3`/`share` | `occupations` sorted descending |
| `cite` | `format` `bibtex`/`apa`/`text` | `citation_text`, `bibtex_key` |

Every response includes `citation` (short BibTeX, key `espinal2026delegation`) and
`data_version`. The bundled data is the real ADI v2026.1 (433 ISCO-08 unit groups, 146
countries); a `warning: "SYNTHETIC/PLACEHOLDER data ..."` appears only if the package is pointed
at placeholder CSVs — do not cite those numbers.

## Smoke test

```bash
python herramientas/adi-mcp/cliente_prueba.py        # spawns adi-mcp over stdio, prints tools/list
python -m pytest herramientas/adi-mcp/tests -q
```

Licence: code MIT, data CC-BY 4.0. Repo: https://github.com/Cespial/delegation-divide
