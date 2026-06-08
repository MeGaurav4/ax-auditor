import httpx
from ..models import CheckResult


async def check_error_clarity(client: httpx.AsyncClient, base_url: str) -> CheckResult:
    score = 0.0
    findings = []
    recs = []

    error_endpoints = [
        (f"{base_url.rstrip('/')}/api/nonexistent-12345", 404),
        (f"{base_url.rstrip('/')}/api/", 404),
    ]

    for url, expected_status in error_endpoints:
        try:
            resp = await client.get(url, timeout=10)
            if resp.status_code == expected_status:
                body = resp.text.lower()
                has_message = any(w in body for w in ["message", "error", "detail", "reason"])
                has_code = any(w in body for w in ["code", "status", "type"])

                if has_message and has_code:
                    findings.append(f"Clear error response at {url}: message + code present")
                elif has_message or has_code:
                    findings.append(f"Partial error info at {url}")
                    score += 0.3
                else:
                    findings.append(f"Generic error at {url} — no message or code")
            else:
                findings.append(f"Unexpected status {resp.status_code} at {url}")
        except httpx.RequestError:
            continue

    if findings:
        score = min(len([f for f in findings if "Clear" in f]) / 2 + 0.2, 1.0)

    if score < 0.5:
        recs.append("Return structured JSON errors with 'message' and 'code' fields")
        recs.append("Document all error codes and their meanings")
    else:
        recs.append("Maintain consistent error format across all endpoints")

    return CheckResult(
        name="Error Response Clarity",
        passed=score >= 0.5,
        score=score,
        weight=0.15,
        detail=" | ".join(findings) if findings else "Could not test error responses",
        recommendation=" ".join(recs),
    )
