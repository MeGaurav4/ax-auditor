import httpx
from ..models import CheckResult


async def check_auth_flow(client: httpx.AsyncClient, base_url: str) -> CheckResult:
    score = 0.0
    findings = []
    recs = []

    login_paths = ["/login", "/signin", "/auth", "/api/auth"]
    api_key_indicators = ["api-key", "api_key", "x-api-key", "apikey", "token"]

    found_login = False
    api_key_auth = False

    for path in login_paths:
        try:
            resp = await client.get(f"{base_url.rstrip('/')}{path}", timeout=10, follow_redirects=True)
            if resp.status_code == 200:
                body = resp.text.lower()
                found_login = True
                for kw in api_key_indicators:
                    if kw in body:
                        api_key_auth = True
                        findings.append(f"API key auth mentioned at {path}")
                        break
                break
        except httpx.RequestError:
            continue

    try:
        resp = await client.get(base_url, timeout=10)
        body = resp.text.lower()
        for kw in api_key_indicators:
            if kw in body:
                api_key_auth = True
                findings.append("API key references found on homepage")
                break
    except httpx.RequestError:
        pass

    if api_key_auth:
        score = 0.9
        findings.append("API-key based auth — compatible with AI agents")
        recs.append("Document how to create and manage API keys")
    elif found_login:
        score = 0.4
        findings.append("OAuth/web login detected — may require browser interaction")
        recs.append("Consider adding API key support for agent-only access")
        recs.append("Document service-to-service auth patterns")
    else:
        score = 0.2
        findings.append("No auth mechanism detected at standard paths")
        recs.append("Publish auth documentation for AI agent integration")

    return CheckResult(
        name="Authentication Flow",
        passed=api_key_auth,
        score=score,
        weight=0.15,
        detail=" | ".join(findings),
        recommendation=" ".join(recs),
    )
