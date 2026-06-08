import httpx
from ..models import CheckResult


async def check_headers(client: httpx.AsyncClient, base_url: str) -> CheckResult:
    score = 0.0
    findings = []
    recs = []

    try:
        resp = await client.get(base_url, timeout=10, follow_redirects=True)
        headers = resp.headers

        header_checks = {
            "content-type": ("Content-Type", lambda v: "text/" in v or "application/" in v),
            "rate-limit": ("X-RateLimit-Limit", lambda v: v.isdigit()),
            "rate-remaining": ("X-RateLimit-Remaining", lambda v: v.isdigit()),
            "rate-reset": ("X-RateLimit-Reset", lambda v: True),
            "retry-after": ("Retry-After", lambda v: True),
            "cors": ("Access-Control-Allow-Origin", lambda v: v == "*" or v.startswith("http")),
        }

        for key, (header_name, validator) in header_checks.items():
            value = headers.get(header_name)
            if value and validator(value):
                findings.append(f"{header_name}: {value}")
                score += 1.0 / len(header_checks)
            else:
                if key in ("rate-limit", "rate-remaining"):
                    recs.append(f"Add {header_name} header for agent-friendly rate limiting")

        if "Retry-After" in headers:
            score += 0.5 / len(header_checks)

    except httpx.RequestError as e:
        return CheckResult(
            name="HTTP Headers (Agent-Friendly)",
            passed=False,
            score=0.0,
            weight=0.15,
            detail=f"Failed to reach {base_url}: {e}",
            recommendation="Ensure the service is reachable and returns standard HTTP headers",
        )

    passed = score >= 0.3
    if not recs and passed:
        recs.append("All agent-friendly headers present")

    return CheckResult(
        name="HTTP Headers (Agent-Friendly)",
        passed=passed,
        score=min(score, 1.0),
        weight=0.15,
        detail=" | ".join(findings) if findings else "No agent-friendly headers detected",
        recommendation=" ".join(recs),
        evidence=f"Status: {resp.status_code}, Headers checked: {', '.join(h[1] for h in header_checks.values())}",
    )
