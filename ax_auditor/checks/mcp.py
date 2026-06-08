import httpx
from ..models import CheckResult


async def check_mcp_support(client: httpx.AsyncClient, base_url: str) -> CheckResult:
    score = 0.0
    detail_parts = []
    rec_parts = []

    mcp_paths = [
        "/.well-known/mcp.json",
        "/mcp.json",
        "/mcp",
        "/api/mcp",
        "/.mcp.json",
    ]

    found_mcp = False
    for path in mcp_paths:
        try:
            resp = await client.get(f"{base_url.rstrip('/')}{path}", timeout=10)
            if resp.status_code == 200:
                found_mcp = True
                score = 1.0
                detail_parts.append(f"MCP manifest found at {path}")
                break
        except httpx.RequestError:
            continue

    if found_mcp:
        score = 1.0
        detail_parts.append("MCP server is advertised and reachable")
        rec_parts.append("Consider adding MCP server documentation and usage examples")
    else:
        score = 0.0
        detail_parts.append("No MCP server manifest found at standard paths")
        rec_parts.append("Implement an MCP server to allow AI agents to interact with your service directly")

    return CheckResult(
        name="MCP Server Support",
        passed=found_mcp,
        score=score,
        weight=0.20,
        detail=" | ".join(detail_parts),
        recommendation=" ".join(rec_parts),
        evidence=f"MCP paths checked: {', '.join(mcp_paths)}",
    )
